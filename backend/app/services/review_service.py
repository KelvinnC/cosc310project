import uuid
from typing import List, Dict, Any
from fastapi import HTTPException
from app.schemas.review import Movie, MovieCreate, MovieUpdate
from app.repositories.movie_repo import load_all, save_all

def list_movies() -> List[Movie]:
    return [Movie(**mv) for mv in load_all()]

def create_movie(payload: MovieCreate) -> Movie:
    movies = load_all()
    new_movie_id = str(uuid.uuid4())
    if any(mov.get("id") == new_movie_id for mov in movies):
        raise HTTPException(status_code=409, detail="ID collision; retry")
    new_movie = Movie(id=new_movie_id, title=payload.title.strip(), genre=payload.genre.strip(), release=payload.release, 
                      description=payload.description.strip(), duration=payload.duration)
    movies.append(new_movie.model_dump(mode="json")) #model_dump auto serializes fields like dates
    save_all(movies)
    return new_movie

def get_movie_by_id(movie_id: str) -> Movie:
    movies = load_all()
    for movie in movies:
        if str(movie.get("id")) == movie_id:
            return Movie(**movie)
    raise HTTPException(status_code=404, detail=f"Movie '{movie_id}' not found")

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