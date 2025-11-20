import uuid
from typing import List, Dict, Any
from fastapi import HTTPException
from app.schemas.movie import Movie, MovieCreate, MovieUpdate, MovieSummary, MovieWithReviews
import app.repositories.movie_repo as movie_repo
from app.repositories.review_repo import load_all as load_reviews
from app.utils.list_helpers import find_dict_by_id, NOT_FOUND


def load_all() -> List[Dict[str, Any]]:
    return movie_repo.load_all()


def save_all(movies: List[Dict[str, Any]]) -> None:
    movie_repo.save_all(movies)


def list_movies(sort_by: str | None = None, order: str = "asc") -> List[Movie]:
    movies: List[Dict[str, Any]] = load_all()

    if sort_by == "rating":
        direction = (order or "asc").lower()
        reverse = direction == "desc"

        reviews_data = load_reviews()
        if reviews_data:
            movie_ids = {mv.get("id") for mv in movies}

            rating_sums: Dict[str, float] = {}
            rating_counts: Dict[str, int] = {}

            for rv in reviews_data:
                mv_id = rv.get("movieId")
                if not isinstance(mv_id, str) or mv_id not in movie_ids:
                    continue

                try:
                    rating_val = float(rv.get("rating"))
                except (TypeError, ValueError):
                    continue

                rating_sums[mv_id] = rating_sums.get(mv_id, 0.0) + rating_val
                rating_counts[mv_id] = rating_counts.get(mv_id, 0) + 1

            avg_ratings: Dict[str, float] = {
                movie_id: rating_sums[movie_id] / rating_counts[movie_id]
                for movie_id in rating_sums
                if rating_counts.get(movie_id)
            }

            for mv in movies:
                mv_id = mv.get("id")
                if mv_id in avg_ratings and mv.get("rating") is None:
                    mv["rating"] = avg_ratings[mv_id]

        def _rating_key(m: Dict[str, Any]):
            val = m.get("rating")
            try:
                return float(val)
            except (TypeError, ValueError):
                return float("-inf") if not reverse else float("inf")

        movies = sorted(movies, key=_rating_key, reverse=reverse)

    return [Movie(**mv) for mv in movies]


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

def get_movie_by_id(movie_id: str) -> MovieWithReviews:
    movies = load_all()
    target_index = find_dict_by_id(movies, "id", movie_id)
    if target_index == NOT_FOUND:
        raise HTTPException(status_code=404, detail=f"Movie '{movie_id}' not found")

    target = movies[target_index]
    reviews_data = load_reviews()
    reviews_list = []
    for rv in reviews_data:
        mv_id = rv.get("movieId")
        if isinstance(mv_id, str) and mv_id == movie_id:
            reviews_list.append(rv)

    wrapped_reviews = [rv for rv in reviews_list]

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
    index = find_dict_by_id(movies, "id", movie_id)
    if index == NOT_FOUND:
        return []
    mv = movies[index]
    return [MovieSummary(id=mv.get("id"), title=mv.get("title"))]

def update_movie(movie_id: str, payload: MovieUpdate) -> Movie:
    movies = load_all()
    index = find_dict_by_id(movies, "id", movie_id)
    if index == NOT_FOUND:
        raise HTTPException(status_code=404, detail=f"Movie '{movie_id}' not found")
    updated = Movie(id=movie_id, title=payload.title.strip(), genre=payload.genre.strip(), release=payload.release, 
                    description=payload.description.strip(), duration=payload.duration)
    movies[index] = updated.model_dump(mode="json")
    save_all(movies)
    return updated

def delete_movie(movie_id: str) -> None:
    movies = load_all()
    new_movies = [movie for movie in movies if movie.get("id") != movie_id]
    if len(new_movies) == len(movies):
        raise HTTPException(status_code=404, detail=f"Movie '{movie_id}' not found")
    save_all(new_movies)
