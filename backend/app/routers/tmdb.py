from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any
from app.services.tmdb_service import search_tmdb_movies, get_tmdb_movie_details, create_tmdb_movie_id

router = APIRouter(prefix="/tmdb", tags=["TMDb External Movies"])


@router.get("/search", response_model=List[Dict[str, Any]])
async def search_external_movies(
    query: str = Query(..., min_length=1, description="Movie title to search for")
):
    """Search TMDb directly. Use /movies/search/all for smart local+external search."""
    results = await search_tmdb_movies(query)
    for movie in results:
        movie["movie_id"] = create_tmdb_movie_id(movie["tmdb_id"])
    return results


@router.get("/movie/{tmdb_id}")
async def get_external_movie_details(tmdb_id: int):
    """Get detailed movie info from TMDb."""
    details = await get_tmdb_movie_details(tmdb_id)
    if not details:
        raise HTTPException(status_code=404, detail="Movie not found on TMDb")
    details["movie_id"] = create_tmdb_movie_id(tmdb_id)
    return details
