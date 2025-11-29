"""Unified movie search - local database with TMDb fallback."""
from typing import List, Dict, Any
from app.services.movie_service import search_movies_titles
from app.services.tmdb_service import search_tmdb_movies, create_tmdb_movie_id

LOCAL_RESULT_THRESHOLD = 3


async def search_all_movies(query: str) -> Dict[str, Any]:
    """Search local DB first; include TMDb results if local results < 3."""
    q = (query or "").strip()
    if not q:
        return {"local": [], "external": [], "source": "local"}
    
    # Search local database first
    local_results = search_movies_titles(q)
    
    # Convert to dict format with source marker
    local_movies = [
        {
            "movie_id": movie.id,
            "title": movie.title,
            "source": "local"
        }
        for movie in local_results
    ]
    
    if len(local_movies) >= LOCAL_RESULT_THRESHOLD:
        return {"local": local_movies, "external": [], "source": "local"}
    
    try:
        tmdb_results = await search_tmdb_movies(q)
        external_movies = [
            {
                "movie_id": create_tmdb_movie_id(movie["tmdb_id"]),
                "title": movie["title"],
                "overview": movie.get("overview", ""),
                "release_date": movie.get("release_date", ""),
                "poster_path": movie.get("poster_path"),
                "source": "tmdb"
            }
            for movie in tmdb_results
        ]
        return {
            "local": local_movies,
            "external": external_movies,
            "source": "both" if local_movies else "tmdb"
        }
    except Exception:
        return {"local": local_movies, "external": [], "source": "local"}
