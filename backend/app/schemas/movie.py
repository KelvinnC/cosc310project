from pydantic import BaseModel
from typing import List
from datetime import date
from .review import Review

class Movie(BaseModel):
    id: str
    title: str
    description: str
    duration: int
    genre: str
    release: date

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


class MovieWithReviews(Movie):
    reviews: List[Review] = []
