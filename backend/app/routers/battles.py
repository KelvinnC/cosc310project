from functools import lru_cache
from pathlib import Path
import random
from typing import List

import orjson
from fastapi import APIRouter, HTTPException, status, Response

from app.schemas.battle import Battle, VoteRequest
from app.schemas.review import Review
from app.services import battle_service
from app.services.user_service import get_user_by_id
from app.repositories import battle_repo


router = APIRouter(prefix="/battles", tags=["battles"])

## TODO: Replace with Review service implementation 
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

## TODO: Replace with Review service implementation 
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

@router.post("/users/{user_id}/battles", response_model=Battle, status_code=201)
def create_battle(user_id: str, response: Response) -> Battle:
    """
    Create a new battle for the user.
    
    RESTful endpoint: POST /battles/users/{user_id}/battles
    Returns 201 Created with Location header pointing to the battle resource.
    """
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
        battle = battle_service.createBattle(user, reviews)
        # Persist the created battle so the resource at Location exists.
        # Convert datetimes to ISO strings for JSON persistence.
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
            # Persist failure: raise 500 since creation cannot be completed atomically
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to persist created battle: {str(e)}",
            )

        # Set Location header to point to the created resource
        response.headers["Location"] = f"/battles/{battle.id}"
        return battle
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/battles/{battle_id}/votes", status_code=204)
def submit_vote(battle_id: str, user_id: str, payload: VoteRequest) -> None:
    """
    Submit a vote for a battle.
    
    RESTful endpoint: POST /battles/{battle_id}/votes
    Returns 204 No Content on success.
    Requires user_id as query parameter (would typically come from auth token).
    """
    # Validate user exists
    user = get_user_by_id(user_id)
    
    # Load the battle by ID
    battle_dict = battle_repo.get_by_id(battle_id)
    if not battle_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Battle {battle_id} not found"
        )
    
    # Convert to Battle object for service layer
    try:
        battle = Battle(**battle_dict)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invalid battle data: {str(e)}"
        )
    
    # Submit the vote
    try:
        battle_service.submitBattleResult(
            battle=battle,
            winner_id=payload.winnerId,
            user_id=user_id
        )
    except ValueError as e:
        if "already voted" in str(e).lower():
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
