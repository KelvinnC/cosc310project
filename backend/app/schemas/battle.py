from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator, ValidationInfo


class Battle(BaseModel):
    """Represents a battle between two reviews from any movie"""
    id: str # UUID
    review1Id: int
    review2Id: int
    winnerId: Optional[int] = None # No winner until a vote is cast
    startedAt: datetime
    endedAt: Optional[datetime] = None # Ends when a vote is cast

    @field_validator('review2Id')
    @classmethod
    def reviews_must_be_different(cls, v: int, info: ValidationInfo) -> int:
        """Ensure review1Id and review2Id are different."""
        review1_id = info.data.get('review1Id')
        if review1_id is not None and v == review1_id:
            raise ValueError('Battle must have two different reviews')
        return v


class VoteRequest(BaseModel):
    """RESTful vote submission payload"""
    winnerId: int
