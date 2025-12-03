import random
from typing import List, Tuple

from app.schemas.user import User
from app.schemas.review import Review
from app.repositories import battle_repo
from app.services.review_service import list_reviews


def load_user_battles(user_id: str) -> List[dict]:
    """Load all battles for a specific user."""
    all_battles = battle_repo.load_all() or []
    return [b for b in all_battles if b.get("userId") == user_id]


def get_user_voted_pairs(user_id: str) -> set:
    """Retrieve all review ID pairs that the user has voted on."""
    user_battles = load_user_battles(user_id)
    voted_pairs = set()
    for b in user_battles:
        if b.get("winnerId") is not None:
            voted_pairs.add(frozenset((b["review1Id"], b["review2Id"])))
    return voted_pairs


def is_own_review(user: User, review: Review) -> bool:
    """Check if the review was authored by the given user."""
    return str(review.authorId) == user.id


def filter_eligible_reviews(user: User, reviews: List[Review]) -> List[Review]:
    """Filter out reviews authored by the user."""
    return [r for r in reviews if not is_own_review(user, r)]


def generate_eligible_pairs(reviews: List[Review], voted_pairs: set) -> List[Tuple[int, int]]:
    """Generate all unique unordered pairs that haven't been voted on."""
    eligible_pairs = []
    for i, r1 in enumerate(reviews):
        for r2 in reviews[i + 1:]:
            pair = frozenset((r1.id, r2.id))
            if pair not in voted_pairs:
                eligible_pairs.append((r1.id, r2.id))
    return eligible_pairs


def sample_reviews_for_battle(user_id: str, sample_size: int = 200) -> List[Review]:
    """Sample reviews for battle, excluding those authored by the given user_id."""
    reviews = list_reviews()
    filtered_reviews = [review for review in reviews if str(review.authorId) != user_id]

    if len(filtered_reviews) > sample_size:
        return random.sample(filtered_reviews, sample_size)

    return filtered_reviews


def select_eligible_pair(user: User, reviews: List[Review]) -> Tuple[int, int]:
    """
    Select an eligible review pair for a battle.

    Returns a tuple of (review1_id, review2_id).
    """
    voted_pairs = get_user_voted_pairs(user.id)
    eligible_reviews = filter_eligible_reviews(user, reviews)
    eligible_pairs = generate_eligible_pairs(eligible_reviews, voted_pairs)

    if not eligible_pairs:
        raise ValueError("No eligible review pairs available for this user.")

    return random.choice(eligible_pairs)
