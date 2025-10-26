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




