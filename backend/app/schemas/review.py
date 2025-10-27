from pydantic import BaseModel
from typing import List, Union
from datetime import date

class Review(BaseModel):
    id: int
    movieId: str
    authorId: Union[int, str]  # Accept both int (-1 for system) and str (UUID for users)
    rating: float
    reviewTitle: str
    reviewBody: str
    flagged: bool = False
    votes: int = 0
    date: date

class ReviewCreate(BaseModel):
    movieId: str
    authorId: int
    rating: float
    reviewTitle: str
    reviewBody: str
    date: date

class ReviewUpdate(BaseModel):
    rating: float
    reviewTitle: str
    reviewBody: str
    flagged: bool = False
    votes: int = 0
    date: date

