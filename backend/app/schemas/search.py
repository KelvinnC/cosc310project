from typing import List, Optional
from pydantic import BaseModel, Field
from .movie import Movie
from .review import Review

try:
    from pydantic import field_validator, model_validator, computed_field
except Exception:
    from pydantic import validator as field_validator
    from pydantic import root_validator as model_validator
    def computed_field(*args, **kwargs):
        def wrapper(func):
            return property(func)
        return wrapper


class MovieSearch(BaseModel):
    query: str = Field(min_length=1)
    genre: Optional[str] = None
    min_rating: Optional[float] = Field(default=None, ge=0, le=10)
    max_rating: Optional[float] = Field(default=None, ge=0, le=10)

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("search query must be a non-empty string")
        return v

    @field_validator("genre")
    @classmethod
    def normalize_genre(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        return v or None

    @model_validator(mode="after")
    def validate_rating_bounds(self):
        if self.min_rating is not None and self.max_rating is not None:
            if self.min_rating > self.max_rating:
                raise ValueError("min_rating cannot be greater than max_rating")
        return self

    def title_matches(self, title: str) -> bool:
        return self.query.lower() in (title or "").lower()

    def genre_matches(self, movie_genre: Optional[str]) -> bool:
        if self.genre is None:
            return True
        return (movie_genre or "").strip().lower() == self.genre.strip().lower()

    def rating_matches(self, rating: Optional[float]) -> bool:
        if rating is None:
            return self.min_rating is None and self.max_rating is None
        if self.min_rating is not None and rating < self.min_rating:
            return False
        if self.max_rating is not None and rating > self.max_rating:
            return False
        return True


class MovieSearchResult(BaseModel):
    query: MovieSearch
    results: List[Movie]

    @computed_field
    @property
    def total(self) -> int:
        return len(self.results)


class MovieWithReviews(Movie):
    reviews: List[Review] = []


