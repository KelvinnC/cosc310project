# battle_service.py
from uuid import uuid4
from datetime import datetime
from typing import List

from app.schemas.user import User
from app.schemas.review import Review
from app.schemas.battle import Battle
from app.repositories import battle_repo
from app.utils.list_helpers import find_dict_by_id, NOT_FOUND
from app.services import battle_pair_selector

def _create_battle_object(review1_id: int, review2_id: int) -> Battle:
    """Create a new Battle object with the given review IDs."""
    return Battle(
        id=str(uuid4()),
        review1Id=review1_id,
        review2Id=review2_id,
        startedAt=datetime.now(),
        endedAt=None,
        winnerId=None,
    )

def _battle_to_dict(battle: Battle, user_id: str) -> dict:
    """Convert a Battle object to a dictionary for persistence."""
    return {
        "id": battle.id,
        "review1Id": battle.review1Id,
        "review2Id": battle.review2Id,
        "winnerId": battle.winnerId,
        "userId": user_id,
        "startedAt": battle.startedAt.isoformat(),
        "endedAt": battle.endedAt.isoformat() if battle.endedAt else None,
    }

def _persist_battle(battle_dict: dict) -> None:
    """Persist a battle to storage."""
    try:
        all_battles = list(battle_repo.load_all())
        all_battles.append(battle_dict)
        battle_repo.save_all(all_battles)
    except Exception as e:
        raise Exception(f"Failed to persist created battle: {str(e)}")

def createBattle(user: User, reviews: List[Review]) -> Battle:
    """Create a new battle. Persists the battle to storage."""
    voted_pairs = _get_user_voted_pairs(user.id)
    eligible_reviews = _filter_eligible_reviews(user, reviews)
    eligible_pairs = _generate_eligible_pairs(eligible_reviews, voted_pairs)

    if not eligible_pairs:
        raise ValueError("No eligible review pairs available for this user.")

    review1_id, review2_id = random.choice(eligible_pairs)
    battle = _create_battle_object(review1_id, review2_id)
    battle_dict = _battle_to_dict(battle, user.id)
    _persist_battle(battle_dict)

    return battle

def _validate_winner(battle: Battle, winner_id: int) -> None:
    """Validate that the winner ID is one of the reviews in the battle."""
    if winner_id not in (battle.review1Id, battle.review2Id):
        raise ValueError(f"Winner {winner_id} not in battle {battle.id}")

def _validate_no_duplicate_vote(battle: Battle, user_id: str) -> None:
    """Validate that the user hasn't already voted on this review pair."""
    pair = frozenset((battle.review1Id, battle.review2Id))
    if pair in _get_user_voted_pairs(user_id):
        raise ValueError("User has already voted on this review pair")

def _update_battle_with_result(battle: Battle, winner_id: int, user_id: str) -> None:
    """Update the battle with the vote result and persist to storage."""
    battle_dict = {
        "id": battle.id,
        "review1Id": battle.review1Id,
        "review2Id": battle.review2Id,
        "winnerId": winner_id,
        "userId": user_id,
        "startedAt": battle.startedAt.isoformat(),
        "endedAt": datetime.now().isoformat()
    }
    
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

def _increment_winner_vote_count(winner_id: int) -> None:
    """Increment the vote count for the winning review."""
    try:
        from app.services import review_service
        review_service.increment_vote(winner_id)
    except Exception as e:
        raise ValueError(f"Failed to increment review vote count: {str(e)}")

def submitBattleResult(battle: Battle, winner_id: int, user_id: str) -> None:
    """Submit a battle result. Persists the result to storage."""
    _validate_winner(battle, winner_id)
    _validate_no_duplicate_vote(battle, user_id)
    _update_battle_with_result(battle, winner_id, user_id)
    _increment_winner_vote_count(winner_id)

def get_battle_by_id(battle_id: str) -> Battle:
    """Retrieve a battle by its ID."""
    battles = battle_repo.load_all()
    index = find_dict_by_id(battles, "id", battle_id)
    if index == NOT_FOUND:
        raise ValueError(f"Battle {battle_id} not found")
    return Battle(**battles[index])


