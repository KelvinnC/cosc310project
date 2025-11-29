"""TMDb API integration service."""
import httpx
import os
from typing import Optional, Dict, Any, List
from fastapi import HTTPException

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE_URL = "https://api.themoviedb.org/3"


def _ensure_api_key() -> None:
    """Raise 503 if API key is not configured."""
    if not TMDB_API_KEY:
        raise HTTPException(status_code=503, detail="TMDb API key not configured")


def _is_bearer_token(key: str) -> bool:
    """Check if key is a JWT bearer token (starts with 'eyJ')."""
    return key.startswith("eyJ")


def _get_auth_headers() -> Dict[str, str]:
    """Get auth headers (used for bearer token auth)."""
    if _is_bearer_token(TMDB_API_KEY):
        return {"Authorization": f"Bearer {TMDB_API_KEY}"}
    return {}


def _get_auth_params() -> Dict[str, str]:
    """Get auth params (used for API key auth)."""
    if not _is_bearer_token(TMDB_API_KEY):
        return {"api_key": TMDB_API_KEY}
    return {}


async def _tmdb_get(endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make authenticated GET request to TMDb API."""
    _ensure_api_key()
    request_params = {"language": "en-US", **(params or {}), **_get_auth_params()}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}{endpoint}",
            params=request_params,
            headers=_get_auth_headers(),
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()


async def search_tmdb_movies(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search TMDb for movies by title."""
    try:
        data = await _tmdb_get("/search/movie", {"query": query, "page": 1})
        return [
            {
                "tmdb_id": m.get("id"),
                "title": m.get("title"),
                "overview": m.get("overview", ""),
                "release_date": m.get("release_date", ""),
                "poster_path": m.get("poster_path"),
            }
            for m in data.get("results", [])[:limit]
        ]
    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=f"TMDb API error: {e}")


async def get_tmdb_movie_details(tmdb_id: int) -> Optional[Dict[str, Any]]:
    """Fetch movie details from TMDb by ID."""
    try:
        movie = await _tmdb_get(f"/movie/{tmdb_id}")
        genres = ", ".join(g["name"] for g in movie.get("genres", []))
        return {
            "tmdb_id": movie.get("id"),
            "title": movie.get("title"),
            "description": movie.get("overview", ""),
            "duration": movie.get("runtime", 0),
            "genre": genres or "Unknown",
            "release": movie.get("release_date", ""),
            "poster_path": movie.get("poster_path"),
            "backdrop_path": movie.get("backdrop_path"),
        }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=404, detail=f"Movie not found on TMDb: {e}")


def is_tmdb_movie_id(movie_id: str) -> bool:
    """Check if movie_id is a TMDb ID (format: tmdb_<id>)."""
    return movie_id.startswith("tmdb_")


def extract_tmdb_id(movie_id: str) -> Optional[int]:
    """Extract numeric ID from tmdb_<id> format."""
    if not is_tmdb_movie_id(movie_id):
        return None
    try:
        return int(movie_id.split("_")[1])
    except (IndexError, ValueError):
        return None


def create_tmdb_movie_id(tmdb_id: int) -> str:
    """Create internal movie ID from TMDb ID."""
    return f"tmdb_{tmdb_id}"
