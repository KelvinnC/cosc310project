"""
TMDb API integration service
Fetches movie data from The Movie Database (TMDb) API
"""
import httpx
import os
from typing import Optional, Dict, Any, List
from datetime import date
from fastapi import HTTPException

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE_URL = "https://api.themoviedb.org/3"


def _get_auth_headers() -> Dict[str, str]:
    """
    Get authentication headers for TMDb API
    Supports both API Key and Bearer Token (Read Access Token)
    """
    if TMDB_API_KEY.startswith("eyJ"):  # JWT Bearer token
        return {"Authorization": f"Bearer {TMDB_API_KEY}"}
    return {}  # Will use api_key param instead


def _get_auth_params() -> Dict[str, str]:
    """Get authentication params for TMDb API (for API Key authentication)"""
    if not TMDB_API_KEY.startswith("eyJ"):  # Regular API key
        return {"api_key": TMDB_API_KEY}
    return {}  # Bearer token uses headers instead


async def search_tmdb_movies(query: str) -> List[Dict[str, Any]]:
    """
    Search for movies on TMDb by title
    Returns a list of movies with basic info
    """
    if not TMDB_API_KEY:
        raise HTTPException(
            status_code=503, 
            detail="TMDb API key not configured"
        )
    
    async with httpx.AsyncClient() as client:
        try:
            params = {
                "query": query,
                "language": "en-US",
                "page": 1,
                **_get_auth_params()
            }
            response = await client.get(
                f"{TMDB_BASE_URL}/search/movie",
                params=params,
                headers=_get_auth_headers(),
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Transform TMDb format to our format
            results = []
            for movie in data.get("results", [])[:10]:  # Limit to 10 results
                results.append({
                    "tmdb_id": movie.get("id"),
                    "title": movie.get("title"),
                    "overview": movie.get("overview", ""),
                    "release_date": movie.get("release_date", ""),
                    "poster_path": movie.get("poster_path"),
                })
            return results
            
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=503,
                detail=f"TMDb API error: {str(e)}"
            )


async def get_tmdb_movie_details(tmdb_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch detailed movie information from TMDb by TMDb ID
    """
    if not TMDB_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="TMDb API key not configured"
        )
    
    async with httpx.AsyncClient() as client:
        try:
            params = {
                "language": "en-US",
                **_get_auth_params()
            }
            response = await client.get(
                f"{TMDB_BASE_URL}/movie/{tmdb_id}",
                params=params,
                headers=_get_auth_headers(),
                timeout=10.0
            )
            response.raise_for_status()
            movie = response.json()
            
            # Transform to our movie format
            genres = ", ".join([g["name"] for g in movie.get("genres", [])])
            release_date_str = movie.get("release_date", "")
            
            return {
                "tmdb_id": movie.get("id"),
                "title": movie.get("title"),
                "description": movie.get("overview", ""),
                "duration": movie.get("runtime", 0),
                "genre": genres or "Unknown",
                "release": release_date_str,
                "poster_path": movie.get("poster_path"),
                "backdrop_path": movie.get("backdrop_path"),
            }
            
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=404,
                detail=f"Movie not found on TMDb: {str(e)}"
            )


def is_tmdb_movie_id(movie_id: str) -> bool:
    """
    Check if a movie_id is a TMDb ID (format: tmdb_<id>)
    """
    return movie_id.startswith("tmdb_")


def extract_tmdb_id(movie_id: str) -> Optional[int]:
    """
    Extract numeric TMDb ID from our format (tmdb_12345)
    """
    if is_tmdb_movie_id(movie_id):
        try:
            return int(movie_id.split("_")[1])
        except (IndexError, ValueError):
            return None
    return None


def create_tmdb_movie_id(tmdb_id: int) -> str:
    """
    Create our internal movie ID format from TMDb ID
    """
    return f"tmdb_{tmdb_id}"
