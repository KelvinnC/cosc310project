from pydantic import BaseModel
from typing import List
from datetime import date
try:
    from pydantic import field_validator as _field_validator  # v2
    _P2 = True
except Exception:
    from pydantic import validator as _validator  # v1 fallback
    _P2 = False

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

    if _P2:
        @_field_validator("movieId", mode="before")
        @classmethod
        def _coerce_movie_id(cls, v):
            return None if v is None else str(v)
    else:
        @_validator("movieId", pre=True)
        def _coerce_movie_id_v1(cls, v):
            return None if v is None else str(v)

class ReviewCreate(BaseModel):
    movieId: str
    authorId: str
    rating: float
    reviewTitle: str
    reviewBody: str
    date: date

    if _P2:
        @_field_validator("movieId", mode="before")
        @classmethod
        def _coerce_movie_id(cls, v):
            return None if v is None else str(v)
    else:
        @_validator("movieId", pre=True)
        def _coerce_movie_id_v1(cls, v):
            return None if v is None else str(v)

class ReviewUpdate(BaseModel):
    rating: float
    reviewTitle: str
    reviewBody: str
    flagged: bool = False
    votes: int = 0
    date: date

