# battle_service.py
import random
from uuid import uuid4
from datetime import datetime
from typing import List

from app.schemas.user import User
from app.schemas.review import Review
from app.schemas.battle import Battle
from app.repositories import battle_repo
from app.utils.list_helpers import find_dict_by_id, NOT_FOUND

def _get_user_voted_pairs(user_id: str) -> set:
    """Retrieve all review ID pairs that the user has voted on."""
    voted_pairs = set()
    for b in battle_repo.load_all() or []:
        if b.get("userId") == user_id and b.get("winnerId") is not None:
            voted_pairs.add(frozenset((b["review1Id"], b["review2Id"])) )
    return voted_pairs

def _is_own_review(user: User, review: Review) -> bool:
    """Check if the review was authored by the given user."""
    return str(review.authorId) == user.id

def createBattle(user: User, reviews: List[Review]) -> Battle:
    """Create a new battle. Persists the battle to storage."""
    voted_pairs = _get_user_voted_pairs(user.id)
    eligible_reviews = [r for r in reviews if not _is_own_review(user, r)]

    # Generate all unique unordered pairs and filter out already-voted pairs
    eligible_pairs = []
    for i, r1 in enumerate(eligible_reviews):
        for r2 in eligible_reviews[i + 1 :]:
            pair = frozenset((r1.id, r2.id))
            if pair in voted_pairs:
                continue
            eligible_pairs.append((r1.id, r2.id))

    if not eligible_pairs:
        raise ValueError("No eligible review pairs available for this user.")

    # Persist battle immediately so callers can reference the created resource
    review1Id, review2Id = random.choice(eligible_pairs)
    battle = Battle(
        id=str(uuid4()),
        review1Id=review1Id,
        review2Id=review2Id,
        startedAt=datetime.now(),
        endedAt=None,
        winnerId=None,
    )

    battle_dict = {
        "id": battle.id,
        "review1Id": battle.review1Id,
        "review2Id": battle.review2Id,
        "winnerId": None,
        "userId": user.id,
        "startedAt": battle.startedAt.isoformat(),
        "endedAt": None,
    }

    try:
        all_battles = list(battle_repo.load_all())
        all_battles.append(battle_dict)
        battle_repo.save_all(all_battles)
    except Exception as e:
        # Persist failure, propagate as generic exception so the caller (router)
        # returns an HTTP 500.
        raise Exception(f"Failed to persist created battle: {str(e)}")

    return battle

def submitBattleResult(battle: Battle, winner_id: int, user_id: str) -> None:
    """Submit a battle result. Persists the result to storage."""
    if winner_id not in (battle.review1Id, battle.review2Id):
        raise ValueError(f"Winner {winner_id} not in battle {battle.id}")
    
    pair = frozenset((battle.review1Id, battle.review2Id))
    if pair in _get_user_voted_pairs(user_id):
        raise ValueError("User has already voted on this review pair")
        
    battle_dict = {
        "id": battle.id,
        "review1Id": battle.review1Id,
        "review2Id": battle.review2Id,
        "winnerId": winner_id,
        "userId": user_id,
        "startedAt": battle.startedAt.isoformat(),
        "endedAt": datetime.now().isoformat()
    }
    
    # Update existing battle instead of appending
    try:
        all_battles = list(battle_repo.load_all())
        index = find_dict_by_id(all_battles, "id", battle.id)
        if index == NOT_FOUND:
            all_battles.append(battle_dict)
        else:
            all_battles[index] = battle_dict
        battle_repo.save_all(all_battles)
    except Exception as e:
        raise ValueError(f"Failed to record vote: {str(e)}")
    
    try:
        from app.services import review_service
        review_service.increment_vote(winner_id)
    except Exception as e:
        raise ValueError(f"Failed to increment review vote count: {str(e)}")

def get_battle_by_id(battle_id: str) -> Battle:
    """Retrieve a battle by its ID."""
    battles = battle_repo.load_all()
    index = find_dict_by_id(battles, "id", battle_id)
    if index == NOT_FOUND:
        raise ValueError(f"Battle {battle_id} not found")
    return Battle(**battles[index])


