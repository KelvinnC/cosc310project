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
    return movie_repo.save_all(movies)

def list_movies(sort_by: str | None = None, order: str = "asc") -> List[Movie]:
    movies: List[Dict[str, Any]] = load_all()

    def _coerce_float(v: Any) -> float | None:
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    needs_rating = any(_coerce_float(m.get("rating")) is None for m in movies)
    derived: Dict[str, float] = {}
    if needs_rating:
        reviews = load_reviews()
        index_to_id = {idx + 1: mv.get("id") for idx, mv in enumerate(movies)}
        totals: Dict[str, float] = {}
        counts: Dict[str, int] = {}
        for rv in reviews:
            mv_id = rv.get("movieId")
            rating = _coerce_float(rv.get("rating"))
            if rating is None:
                continue
            if isinstance(mv_id, int):
                movie_id = index_to_id.get(mv_id)
            else:
                movie_id = str(mv_id) if mv_id is not None else None
            if not movie_id:
                continue
            totals[movie_id] = totals.get(movie_id, 0.0) + rating
            counts[movie_id] = counts.get(movie_id, 0) + 1
        for mid, total in totals.items():
            cnt = counts.get(mid) or 0
            if cnt > 0:
                derived[mid] = total / cnt

    enriched: List[Dict[str, Any]] = []
    for m in movies:
        base = dict(m)
        current = _coerce_float(base.get("rating"))
        if current is None:
            comp = derived.get(base.get("id"))
            if comp is not None:
                base["rating"] = comp
        else:
            base["rating"] = current
        enriched.append(base)

    result = enriched
    if sort_by == "rating":
        direction = (order or "asc").lower()
        reverse = (direction == "desc")

        def _rating_key(m: Dict[str, Any]):
            val = _coerce_float(m.get("rating"))
            if val is None:
                return float("-inf") if not reverse else float("inf")
            return val

        result = sorted(enriched, key=_rating_key, reverse=reverse)

    return [Movie(**mv) for mv in result]

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
    index_1_based = target_index + 1
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
