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


"""Deleted redundant schemas below; validation moved to service layer. 
These schemas are not needed because battles are never created directly from user input."""

# class BattleCreate(BaseModel): 
#     """Schema for creating a new battle"""
#     review1Id: int
#     review2Id: int

#     @field_validator('review2Id')
#     def reviewsMustBeDifferent(cls, v, info: ValidationInfo): 
#         review1 = info.data.get('review1Id')
#         if review1 is not None and v == review1:
#             raise ValueError('review2Id must be different from review1Id')
#         return v

# class BattleResult(BaseModel):
#     """Request payload for submitting a vote (legacy, use VoteRequest)"""
#     battle: Battle
#     winnerId: int
    
