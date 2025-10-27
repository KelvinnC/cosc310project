from pydantic import BaseModel
from typing import List
from datetime import date

class Review(BaseModel):
    id: int
    movieId: str
    authorId: int
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

