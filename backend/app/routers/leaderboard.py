from typing import List, Dict, Union

from fastapi import APIRouter

from app.schemas.review import Review
from app.schemas.movie import Movie
from app.services.review_service import get_leaderboard_reviews
from app.services.movie_service import get_leaderboard_movies


router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("", response_model=Dict[str, Union[List[Review], List[Movie]]])
def get_leaderboard(limit: int = 10) -> Dict[str, Union[List[Review], List[Movie]]]:
    reviews = get_leaderboard_reviews(limit=limit)
    movies = get_leaderboard_movies(limit=limit)
    return {"reviews": reviews, "movies": movies}


