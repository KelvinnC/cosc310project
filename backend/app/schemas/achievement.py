from enum import Enum
from typing import Optional
from pydantic import BaseModel


class AchievementCategory(str, Enum):
    MOST_REVIEWS = "most_reviews"
    MOST_VOTES = "most_votes"
    MOST_BATTLES = "most_battles"


class AchievementWinner(BaseModel):
    category: AchievementCategory
    userId: str
    username: str
    value: int
    label: str
    position: int = 1
    tieBreakDate: Optional[str] = None
    medalColor: Optional[str] = None
