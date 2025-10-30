from typing import List, Dict, Set
from app.schemas.search import MovieSearch, MovieWithReviews
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


def search_movies_with_reviews(search: MovieSearch) -> List[MovieWithReviews]:
    movies = load_movies()
    matched_ids: Set[str] = set()
    matched_movies: Dict[str, Dict] = {}
    for mv in movies:
        if search.title_matches(mv.get("title") or ""):
            mid = mv.get("id")
            if isinstance(mid, str):
                matched_ids.add(mid)
                matched_movies[mid] = mv
    if not matched_ids:
        return []

    idx_to_uuid: Dict[int, str] = {idx + 1: m.get("id") for idx, m in enumerate(movies) if isinstance(m.get("id"), str)}

    buckets: Dict[str, List[Review]] = {mid: [] for mid in matched_ids}
    for rv in load_reviews():
        mv_id = rv.get("movieId")
        uuid = None
        if isinstance(mv_id, str):
            uuid = mv_id
        elif isinstance(mv_id, int):
            uuid = idx_to_uuid.get(mv_id)
            if uuid:
                rv = {**rv, "movieId": uuid}
        else:
            continue
        if uuid in matched_ids:
            try:
                buckets[uuid].append(Review(**rv))
            except Exception:
                continue

    results: List[MovieWithReviews] = []
    for mid in matched_ids:
        mv = matched_movies[mid]
        try:
            results.append(
                MovieWithReviews(
                    id=mv.get("id"),
                    title=mv.get("title"),
                    description=mv.get("description"),
                    duration=mv.get("duration"),
                    genre=mv.get("genre"),
                    release=mv.get("release"),
                    reviews=buckets.get(mid, []),
                )
            )
        except Exception:
            continue
    return results
