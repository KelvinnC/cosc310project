from pydantic import BaseModel
from typing import List
from datetime import date

class Review(BaseModel):
    id: int
    movieId: int
    authorId: int
    rating: float
    reviewTitle: str
    reviewBody: str
    flagged: bool = False
    votes: int = 0
    date: date

class ReviewCreate(BaseModel):
    movieId: int
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

