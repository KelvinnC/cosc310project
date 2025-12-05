from fastapi import APIRouter, status, Query, HTTPException
from typing import List, Dict, Any
from app.schemas.movie import Movie, MovieCreate, MovieUpdate, MovieWithReviews, MovieSummary
from app.services.movie_service import (
    list_movies,
    create_movie,
    delete_movie,
    update_movie,
    get_movie_by_id,
    search_movies_titles,
    movie_summary_by_id,
)
from app.services.unified_search_service import search_all_movies

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("", response_model=List[Movie], summary="List all movies")
def get_movies(sort_by: str | None = Query(None), order: str = Query("asc")):
    """
    Retrieve all movies in the local database.
    
    - **sort_by**: Field to sort by (e.g., 'title', 'year')
    - **order**: Sort order ('asc' or 'desc')
    """
    return list_movies(sort_by=sort_by, order=order)


@router.post("", response_model=Movie, status_code=201, summary="Add a movie")
def post_movie(payload: MovieCreate):
    """Add a new movie to the local database."""
    return create_movie(payload)

@router.get("/search/all", response_model=Dict[str, Any])
async def search_movies_all(title: str = Query(..., min_length=1)):
    """
    Smart search: Searches local database first, then TMDb if needed.
    Returns both local and external results in a structured format.
    """
    return await search_all_movies(title)

@router.get("/search", response_model=List[MovieSummary])
def search_movies(title: str = Query(..., min_length=1)):
    """
    Search local movie database only.
    For a smarter search that includes TMDb, use /movies/search/all
    """
    return search_movies_titles(title)

@router.get("/search/", include_in_schema=False, response_model=List[MovieSummary])
def search_movies_slash(title: str = Query(..., min_length=1)):
    return search_movies_titles(title)

@router.get("/{movie_id}", response_model=List[MovieWithReviews], summary="Get movie with reviews")
def get_movie(movie_id: str):
    """
    Retrieve a movie by ID along with all its reviews.
    
    Returns an empty list if the movie is not found.
    """
    try:
        return [get_movie_by_id(movie_id)]
    except HTTPException as exc:
        if getattr(exc, "status_code", None) == 404:
            return []
        raise

@router.put("/{movie_id}", response_model=Movie, summary="Update movie")
def put_movie(movie_id: str, payload: MovieUpdate):
    """Update an existing movie's information."""
    return update_movie(movie_id, payload)


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete movie")
def remove_movie(movie_id: str):
    """Permanently delete a movie and all its associated reviews."""
    delete_movie(movie_id)
    return None
