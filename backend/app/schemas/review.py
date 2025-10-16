from pydantic import BaseModel
from typing import List

class Review(BaseModel):
    id: int
    movieId: int
    authorId: int
    rating: float
    reviewTitle: str
    reviewBody: str
    flagged: bool = False
    votes: int = 0

class ReviewCreate(BaseModel):
    movieId: int
    authorId: int
    rating: float
    reviewTitle: str
    reviewBody: str

class ReviewUpdate(BaseModel):
    rating: float
    reviewTitle: str
    reviewBody: str
    flagged: bool = False
    votes: int = 0

