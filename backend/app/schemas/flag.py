from pydantic import BaseModel
from datetime import datetime


class Flag(BaseModel):
    """Represents a user's flag on a review"""
    user_id: str
    review_id: int
    timestamp: datetime
