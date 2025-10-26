from typing import List, Dict, Any, Set
from app.schemas.search import MovieSearch
from app.schemas.review import Review
from app.repositories.movie_repo import load_all as load_movies
from app.repositories.review_repo import load_all as load_reviews


def _matching_movie_ids(search: MovieSearch) -> Set[int]:
    movies = load_movies()
    match_ids: Set[int] = set()
    for idx, mv in enumerate(movies):
        title = mv.get("title") or ""
        if search.title_matches(title):
            match_ids.add(idx + 1)
    return match_ids


def search_reviews_by_title(search: MovieSearch) -> List[Review]:
    movie_ids = _matching_movie_ids(search)
    if not movie_ids:
        return []

    reviews_data: List[Dict[str, Any]] = load_reviews()
    results: List[Review] = []
    for rv in reviews_data:
        try:
            if int(rv.get("movieId")) in movie_ids:
                results.append(Review(**rv))
        except Exception:
            continue
    return results

