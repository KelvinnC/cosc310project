from typing import List, Dict, Set
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


def _iter_matching_reviews(search: MovieSearch, *, page: int, per_page: int) -> List[Review]:
    movies = load_movies()
    matched_movie_ids = _matching_movie_ids(search)
    if not matched_movie_ids:
        return []

    idx_to_uuid: Dict[int, str] = {idx + 1: mv.get("id") for idx, mv in enumerate(movies) if isinstance(mv.get("id"), str)}

    start = (page - 1) * per_page
    taken = 0
    seen = 0
    results: List[Review] = []

    for rv in load_reviews():
        movie_id = rv.get("movieId")
        uuid = None
        if isinstance(movie_id, str):
            uuid = movie_id
        elif isinstance(movie_id, int):
            uuid = idx_to_uuid.get(movie_id)
        else:
            continue
        if uuid not in matched_movie_ids:
            continue
        if seen < start:
            seen += 1
            continue
        rv_out = rv if isinstance(movie_id, str) else {**rv, "movieId": uuid}
        results.append(Review(**rv_out))
        taken += 1
        seen += 1
        if taken >= per_page:
            return results
    return results


def all_matching_reviews(search: MovieSearch) -> List[Review]:
    movies = load_movies()
    matched_movie_ids = _matching_movie_ids(search)
    if not matched_movie_ids:
        return []

    idx_to_uuid: Dict[int, str] = {idx + 1: mv.get("id") for idx, mv in enumerate(movies) if isinstance(mv.get("id"), str)}

    results: List[Review] = []
    for rv in load_reviews():
        movie_id = rv.get("movieId")
        uuid = None
        if isinstance(movie_id, str):
            uuid = movie_id
        elif isinstance(movie_id, int):
            uuid = idx_to_uuid.get(movie_id)
        else:
            continue
        if uuid not in matched_movie_ids:
            continue
        rv_out = rv if isinstance(movie_id, str) else {**rv, "movieId": uuid}
        results.append(Review(**rv_out))
    return results


def search_reviews_by_title(search: MovieSearch, *, page: int = 1, per_page: int = 50) -> List[Review]:
    return _iter_matching_reviews(search, page=page, per_page=per_page)
