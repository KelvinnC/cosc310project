from fastapi import APIRouter, HTTPException, status, Response, Depends

from app.schemas.watchlist import Watchlist, WatchlistRequest
from app.schemas.movie import MovieCreate
from app.services.watchlist_service import add_movie_to_user_watchlist, get_watchlist_by_author_id
from app.middleware.auth_middleware import jwt_auth_dependency

router = APIRouter(prefix="/watchlist", tags=["watchlist"])

from pydantic import BaseModel

# 1. Define the schema for the body


@router.post("/add", response_model=Watchlist, status_code=201)
def post_watchlist(movieId: str, current_user: dict = Depends(jwt_auth_dependency)):
    authorId = current_user.get("user_id")
    return add_movie_to_user_watchlist(author_id=authorId, movie_id=movieId)

@router.get("", response_model=Watchlist, status_code=201)
def get_watchlist(current_user: dict = Depends(jwt_auth_dependency)):
    authorId = current_user.get("user_id")
    return get_watchlist_by_author_id(author_id=authorId)
