from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from .review import Review

class Movie(BaseModel):
    id: str
    title: str
    description: str
    duration: int
    genre: str
    release: date
    rating: Optional[float] = None

class MovieCreate(BaseModel):
    title: str
    genre: str
    release: date
    description: str
    duration: int

class MovieUpdate(BaseModel):
    title: str
    genre: str
    release: date
    description: str
    duration: int


class MovieSummary(BaseModel):
    id: str
    title: str
    release: Optional[date] = None


class MovieWithReviews(Movie):
    reviews: List[Review] = []
