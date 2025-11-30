from typing import List

from fastapi import APIRouter

from app.schemas.review import Review
from app.services.review_service import get_leaderboard_reviews


router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("", response_model=List[Review])
def get_leaderboard(limit: int = 10) -> List[Review]:
    return get_leaderboard_reviews(limit=limit)
