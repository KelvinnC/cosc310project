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
    

"""Deleted redundant schemas below; validation moved to service layer. 
These schemas are not needed because battles are never created directly from user input."""

# class BattleResult(BaseModel):
#     """Schema for submitting a vote in a battle"""
#     battleId: str # UUID
#     winnerId: int

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
    
