from fastapi import APIRouter, HTTPException, status
from pathlib import Path
import json

from app.schemas.battle import Battle, BattleResult
from app.schemas.review import Review
from app.services import battle_service
from app.services.user_service import get_user_by_id

router = APIRouter(prefix="/battles", tags=["battles"])


@router.post("/{user_id}/create", response_model=Battle, status_code=201)
def create_battle(user_id: str):
    """Generate a new battle for the user."""
    user = get_user_by_id(user_id)
    
    # TODO: Replace with review_service.load_all() once implemented by @drabenstien
    # ----------------------------------------------------------------------------

    data_path = Path(__file__).resolve().parents[1] / "data" / "reviews.json"
    if not data_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reviews available"
        )
    
    with data_path.open("r", encoding="utf-8") as f:
        reviews_data = json.load(f)
    reviews = [Review(**r) for r in reviews_data]

    # ----------------------------------------------------------------------------

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
def submit_vote(user_id: str, payload: BattleResult):
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
