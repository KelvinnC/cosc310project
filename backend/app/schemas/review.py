from pydantic import BaseModel, Field
from typing import Union
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
    rating: float
    reviewTitle: str = Field(..., min_length=3, max_length=100)
    reviewBody: str = Field(..., min_length=50, max_length=1000)

    if _P2:
        @_field_validator("movieId", mode="before")
        @classmethod
        def _coerce_movie_id(cls, v):
            return None if v is None else str(v)
        @_field_validator("rating", mode="before")
        @classmethod
        def _cap_rating(cls, v):
            try:
                val = float(v)
            except Exception:
                return v
            if val < 1:
                return 1.0
            if val > 5:
                return 5.0
            return val
        @_field_validator("reviewTitle", "reviewBody", mode="before")
        @classmethod
        def _strip_text(cls, v):
            return v.strip() if isinstance(v, str) else v
    else:
        @_validator("movieId", pre=True)
        def _coerce_movie_id_v1(cls, v):
            return None if v is None else str(v)
        @_validator("rating", pre=True)
        def _cap_rating_v1(cls, v):
            try:
                val = float(v)
            except Exception:
                return v
            if val < 1:
                return 1.0
            if val > 5:
                return 5.0
            return val
        @_validator("reviewTitle", "reviewBody", pre=True)
        def _strip_text_v1(cls, v):
            return v.strip() if isinstance(v, str) else v

class ReviewUpdate(BaseModel):
    rating: float
    reviewTitle: str
    reviewBody: str
    flagged: bool = False
    votes: int = 0
    date: date

