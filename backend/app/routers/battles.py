from functools import lru_cache
from pathlib import Path
import random
from typing import List

import orjson
from fastapi import APIRouter, HTTPException, status

from app.schemas.battle import Battle, BattleResult
from app.schemas.review import Review
from app.services import battle_service
from app.services.user_service import get_user_by_id


router = APIRouter(prefix="/battles", tags=["battles"])

## TODO: Replace with Review service implementation when available 
@lru_cache(maxsize=1)
def _load_reviews_raw():
    """
    Load raw review data from JSON file once using 
    fast orjson parser and cache in memory.
    """
    data_path = Path(__file__).resolve().parents[1] / "data" / "reviews.json"
    if not data_path.exists():
        raise FileNotFoundError("reviews.json not found")
    with data_path.open("rb") as f:
        return orjson.loads(f.read())


def _sample_reviews_for_battle(user_id: str, sample_size: int = 200) -> List[Review]:
    """
    Sample a subset of reviews for battle creation to avoid converting all 
    517k into Review objects.
    """
    reviews_data = _load_reviews_raw()
    
    if len(reviews_data) > sample_size:
        sampled_data = random.sample(reviews_data, sample_size)
    else:
        sampled_data = reviews_data
    return [Review(**r) for r in sampled_data]

@router.post("/{user_id}/create", response_model=Battle, status_code=201)
def create_battle(user_id: str) -> Battle:
    """Generate a new battle for the user."""
    user = get_user_by_id(user_id)

    try:
        ## TODO: Replace _sample_reviews_for_battle with Review service implementation
        reviews = _sample_reviews_for_battle(user_id, sample_size=200) 
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reviews available"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load reviews: {str(e)}"
        )

    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reviews available"
        )
    
    try:
        return battle_service.createBattle(user, reviews)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{user_id}/vote", status_code=204)
def submit_vote(user_id: str, payload: BattleResult) -> None:
    """Submit vote for a battle."""
    user = get_user_by_id(user_id)
    
    try:
        battle_service.submitBattleResult(
            battle=payload.battle,
            winner_id=payload.winnerId,
            user_id=user_id
        )
    except ValueError as e:
        if "already voted" in str(e).lower():
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    
    return
