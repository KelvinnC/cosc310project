"""
Unified movie search service - searches local database and TMDb
"""
from typing import List, Dict, Any
from app.services.movie_service import search_movies_titles
from app.services.tmdb_service import search_tmdb_movies, create_tmdb_movie_id


async def search_all_movies(query: str) -> Dict[str, Any]:
    """
    Search for movies in both local database and TMDb.
    Returns local results first, then TMDb results if local search has few results.
    
    Returns:
        {
            "local": [...],      # Movies from local database
            "external": [...],   # Movies from TMDb (if needed)
            "source": "local" | "both"
        }
    """
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
    
    # If we have enough local results (3+), only return those
    if len(local_movies) >= 3:
        return {
            "local": local_movies,
            "external": [],
            "source": "local"
        }
    
    # Otherwise, also search TMDb
    try:
        tmdb_results = await search_tmdb_movies(q)
        
        # Format TMDb results
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
        # If TMDb search fails, just return local results
        return {
            "local": local_movies,
            "external": [],
            "source": "local"
        }
