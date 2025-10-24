# battle_service.py
import random
from uuid import uuid4
from datetime import datetime
from typing import List

from app.schemas.user import User
from app.schemas.review import Review
from app.schemas.battle import Battle
from app.repositories import battle_repo


def createBattle(user: User, reviews: List[Review]) -> Battle:
    """
    Generate a battle between two reviews for a user to vote on.
    
    Creates a battle by selecting two reviews the user hasn't voted on before,
    excluding their own reviews. Uses the user's `votedBattles` to avoid
    showing previously-decided pairs. Returns a Battle object but does not
    persist it; the battle is saved when a vote is submitted.

    Args:
        user: User requesting the battle
        reviews: Available review pool
    
    Returns:
        New Battle object ready for voting
    
    Raises:
        ValueError: If no eligible pairs exist (all voted or only own reviews)
    """
    # Get all existing battles
    all_battles = list(battle_repo.load_all())

    # Build set of review-id pairs the user has already voted on using
    # user's `votedBattles` list of battle ids.
    user_battle_ids = set(getattr(user, "votedBattles", []))
    user_battles = [b for b in all_battles if b.get("id") in user_battle_ids]
    voted_pairs = {frozenset((b["review1Id"], b["review2Id"])) for b in user_battles}

    # Filter out user's own reviews
    eligible_reviews = [r for r in reviews if r.id not in set(user.ownReviewIds)]

    # Generate all unique unordered pairs from eligible reviews and filter out
    # pairs the user has already voted on
    eligible_pairs = []
    for i, r1 in enumerate(eligible_reviews):
        for r2 in eligible_reviews[i + 1 :]:
            pair = frozenset((r1.id, r2.id))
            if pair in voted_pairs:
                continue
            eligible_pairs.append((r1.id, r2.id))

    if not eligible_pairs:
        raise ValueError("No eligible review pairs available for this user.")

    # Randomly choose a pair and return a Battle object. 
    review1Id, review2Id = random.choice(eligible_pairs)
    battle = Battle(
        id=str(uuid4()),
        review1Id=review1Id,
        review2Id=review2Id,
        startedAt=datetime.now(),
        endedAt=None,
        winnerId=None,
    )

    return battle


def submitBattleResult(battle: Battle, winner_id: int, user_id: str) -> None:
    """Record a user's vote by persisting the battle with its winner.
    
    Args:
        battle: The battle to persist with the vote result
        winner_id: The ID of the winning review
        user_id: ID of the user submitting this vote
        
    Raises:
        ValueError: if winner_id is not one of the battle's reviews
    """
    # Validate winner is one of the battle reviews
    if winner_id not in (battle.review1Id, battle.review2Id):
        raise ValueError(f"Winner {winner_id} not in battle {battle.id}")
        
    # Prepare battle data
    battle_dict = battle.model_dump()
    battle_dict.update({
        "userId": user_id,
        "winnerId": winner_id,
        "endedAt": datetime.now().isoformat()
    })
    
    # Update repositories atomically
    try:
        # Save battle result
        all_battles = list(battle_repo.load_all())
        all_battles.append(battle_dict)
        battle_repo.save_all(all_battles)
        
        # Update user's vote history
        from app.services.user_service import get_user_by_id, update_user_state
        user = get_user_by_id(user_id)
        if not hasattr(user, "votedBattles"):
            user.votedBattles = []
        user.votedBattles.append(battle.id)
        update_user_state(user)
            
    except Exception as e:
        raise ValueError(f"Failed to record vote: {str(e)}")


