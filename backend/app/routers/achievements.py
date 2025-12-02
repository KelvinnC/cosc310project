from typing import List
from fastapi import APIRouter

from app.schemas.achievement import AchievementWinner
from app.services.achievement_service import get_achievement_winners


router = APIRouter(prefix="/achievements", tags=["achievements"])


@router.get("", response_model=List[AchievementWinner])
def list_achievements() -> List[AchievementWinner]:
    return get_achievement_winners()
