# battle_service.py
import random
from uuid import uuid4
from datetime import datetime
from typing import List

from app.schemas.user import User
from app.schemas.review import Review
from app.schemas.battle import Battle
from app.repositories import battle_repo

def _get_user_voted_pairs(user_id: str) -> set:
    """Return set of unordered pairs the user has already voted on.

    Uses battles persisted with userId == user_id and a winner set, validating the vote is complete.
    Each pair is represented as frozenset({review1Id, review2Id}).
    """
    voted_pairs = set()
    for b in battle_repo.load_all() or []:
        if b.get("userId") == user_id and b.get("winnerId") is not None:
            voted_pairs.add(frozenset((b["review1Id"], b["review2Id"])) )
    return voted_pairs

def _is_own_review(user: User, review: Review) -> bool:
    """Check if the review was authored by the given user."""
    return str(review.authorId) == user.id

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
    # Build set of review-id pairs the user has already voted on by scanning battles
    voted_pairs = _get_user_voted_pairs(user.id)

    # Filter out user's own reviews via authorId comparison
    eligible_reviews = [r for r in reviews if not _is_own_review(user, r)]

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




