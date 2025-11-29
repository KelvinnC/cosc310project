"""
TMDb API router - endpoints for searching external movies
"""
from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any
from app.services.tmdb_service import search_tmdb_movies, get_tmdb_movie_details, create_tmdb_movie_id
from app.services.unified_search_service import search_all_movies

router = APIRouter(prefix="/tmdb", tags=["TMDb External Movies"])


@router.get("/search/unified", response_model=Dict[str, Any])
async def search_movies_unified(
    query: str = Query(..., min_length=1, description="Movie title to search for")
):
    """
    Unified movie search - searches local database first, then TMDb if needed.
    
    Returns:
    - local: Movies from your database
    - external: Movies from TMDb (included if local results < 3)
    - source: "local", "tmdb", or "both"
    
    This is the recommended search endpoint for a better user experience.
    """
    return await search_all_movies(query)


@router.get("/search", response_model=List[Dict[str, Any]])
async def search_external_movies(
    query: str = Query(..., min_length=1, description="Movie title to search for")
):
    """
    Search for movies on TMDb only.
    Returns movies that aren't in our local database.
    Users can write reviews for these movies using the tmdb_<id> format.
    
    Note: Consider using /tmdb/search/unified for a better experience.
    """
    results = await search_tmdb_movies(query)
    
    # Add our internal movie_id format
    for movie in results:
        movie["movie_id"] = create_tmdb_movie_id(movie["tmdb_id"])
    
    return results


@router.get("/movie/{tmdb_id}")
async def get_external_movie_details(tmdb_id: int):
    """
    Get detailed information about a TMDb movie
    """
    details = await get_tmdb_movie_details(tmdb_id)
    if not details:
        raise HTTPException(status_code=404, detail="Movie not found on TMDb")
    
    # Add our internal movie_id
    details["movie_id"] = create_tmdb_movie_id(tmdb_id)
    return details
