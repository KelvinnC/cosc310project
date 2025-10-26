from typing import List, Dict, Any, Set
from app.schemas.search import MovieSearch
from app.schemas.review import Review
from app.repositories.movie_repo import load_all as load_movies
from app.repositories.review_repo import load_all as load_reviews


def _matching_movie_ids(search: MovieSearch) -> Set[str]:
    movies = load_movies()
    match_ids: Set[str] = set()
    for mv in movies:
        title = mv.get("title") or ""
        if search.title_matches(title):
            mid = mv.get("id")
            if isinstance(mid, str):
                match_ids.add(mid)
    return match_ids


def search_reviews_by_title(search: MovieSearch) -> List[Review]:
    movies = load_movies()
    matched_movie_ids = _matching_movie_ids(search)
    if not matched_movie_ids:
        return []

    idx_to_uuid: Dict[int, str] = {idx + 1: mv.get("id") for idx, mv in enumerate(movies) if isinstance(mv.get("id"), str)}

    results: List[Review] = []
    for rv in load_reviews():
        movie_id = rv.get("movieId")
        # UUID
        if isinstance(movie_id, str):
            if movie_id in matched_movie_ids:
                results.append(Review(**rv))
            continue
        # Legacy
        if isinstance(movie_id, int):
            uuid = idx_to_uuid.get(movie_id)
            if uuid and uuid in matched_movie_ids:
                rv_copy = dict(rv)
                rv_copy["movieId"] = uuid
                results.append(Review(**rv_copy))
            continue
    return results
