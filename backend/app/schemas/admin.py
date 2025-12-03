from pydantic import BaseModel
from typing import List, Any


class AdminSummaryResponse(BaseModel):
    total_users: int
    warned_users: List[Any]
    banned_users: List[Any]
    flagged_reviews: List[Any]
