from pydantic import BaseModel
from typing import List
from datetime import date
from .review import Review

class Movie(BaseModel):
    id: int
    title: str
    genre: str
    release: date
    reviews: List[Review] = []

class MovieCreate(BaseModel):
    title: str
    genre: str
    release: date

class MovieUpdate(BaseModel):
    title: str
    genre: str
    release: date