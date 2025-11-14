import uuid
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from datetime import date as date_type
from app.schemas.movie import Movie, MovieCreate, MovieUpdate, MovieSummary, MovieWithReviews
from app.repositories.movie_repo import load_all, save_all
from app.repositories.review_repo import load_all as load_reviews
from app.services.tmdb_service import (
    get_tmdb_movie_details, 
    is_tmdb_movie_id, 
    extract_tmdb_id
)

def list_movies() -> List[Movie]:
    return [Movie(**mv) for mv in load_all()]

def create_movie(payload: MovieCreate) -> Movie:
    movies = load_all()
    new_movie_id = str(uuid.uuid4())
    if any(mov.get("id") == new_movie_id for mov in movies):
        raise HTTPException(status_code=409, detail="ID collision; retry")
    new_movie = Movie(id=new_movie_id, title=payload.title.strip(), genre=payload.genre.strip(), release=payload.release, 
                      description=payload.description.strip(), duration=payload.duration)
    movies.append(new_movie.model_dump(mode="json"))
    save_all(movies)
    return new_movie

async def get_movie_by_id(movie_id: str) -> MovieWithReviews:
    """
    Get movie by ID - supports both local movies and TMDb movies
    If movie_id starts with 'tmdb_', fetch from TMDb API
    """
    # Check if this is a TMDb movie
    if is_tmdb_movie_id(movie_id):
        tmdb_id = extract_tmdb_id(movie_id)
        if tmdb_id is None:
            raise HTTPException(status_code=400, detail="Invalid TMDb movie ID format")
        
        # Fetch from TMDb API
        tmdb_data = await get_tmdb_movie_details(tmdb_id)
        if not tmdb_data:
            raise HTTPException(status_code=404, detail=f"TMDb movie '{movie_id}' not found")
        
        # Parse release date
        try:
            release_date = date_type.fromisoformat(tmdb_data["release"])
        except (ValueError, KeyError):
            release_date = date_type(1900, 1, 1)
        
        target = {
            "id": movie_id,
            "title": tmdb_data["title"],
            "description": tmdb_data["description"],
            "duration": tmdb_data["duration"],
            "genre": tmdb_data["genre"],
            "release": release_date,
        }
        
        # Get reviews for this TMDb movie (stored locally)
        reviews_data = load_reviews()
        reviews_list = [rv for rv in reviews_data if rv.get("movieId") == movie_id]
        
        return MovieWithReviews(**target, reviews=reviews_list)
    
    # Local movie lookup
    movies = load_all()
    target = None
    target_index = None
    for idx, movie in enumerate(movies):
        if str(movie.get("id")) == movie_id:
            target = movie
            target_index = idx
            break
    if target is None:
        raise HTTPException(status_code=404, detail=f"Movie '{movie_id}' not found")

    index_1_based = (target_index or 0) + 1
    reviews_data = load_reviews()
    reviews_list = []
    for rv in reviews_data:
        mv_id = rv.get("movieId")
        if isinstance(mv_id, str) and mv_id == movie_id:
            reviews_list.append(rv)
        elif isinstance(mv_id, int) and mv_id == index_1_based:
            reviews_list.append({**rv, "movieId": movie_id})

    wrapped_reviews = [
        rv
        for rv in reviews_list
    ]

    return MovieWithReviews(
        id=target.get("id"),
        title=target.get("title"),
        description=target.get("description"),
        duration=target.get("duration"),
        genre=target.get("genre"),
        release=target.get("release"),
        reviews=wrapped_reviews,
    )

def search_movies_titles(query: str) -> List[MovieSummary]:
    q = (query or "").strip().lower()
    if not q:
        return []
    movies = load_all()
    results: List[MovieSummary] = []
    for mv in movies:
        title = (mv.get("title") or "").lower()
        if q in title:
            results.append(MovieSummary(id=mv.get("id"), title=mv.get("title")))
    return results

def movie_summary_by_id(movie_id: str) -> List[MovieSummary]:
    movies = load_all()
    for mv in movies:
        if str(mv.get("id")) == str(movie_id):
            return [MovieSummary(id=mv.get("id"), title=mv.get("title"))]
    return []

def update_movie(movie_id: str, payload: MovieUpdate) -> Movie:
    movies = load_all()
    for idx, movie in enumerate(movies):
        if movie.get("id") == movie_id:
            updated = Movie(id=movie_id, title=payload.title.strip(), genre=payload.genre.strip(), release=payload.release, 
                      description=payload.description.strip(), duration=payload.duration)
            movies[idx] = updated.model_dump(mode="json")
            save_all(movies)
            return updated
    raise HTTPException(status_code=404, detail=f"Movie '{movie_id}' not found")

def delete_movie(movie_id: str) -> None:
    movies = load_all()
    new_movies = [movie for movie in movies if movie.get("id") != movie_id]
    if len(new_movies) == len(movies):
        raise HTTPException(status_code=404, detail=f"Movie '{movie_id}' not found")
    save_all(new_movies)
