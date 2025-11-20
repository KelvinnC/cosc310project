from typing import List, Dict, Set, Tuple, Optional

from app.schemas.search import MovieSearch, MovieWithReviews
from app.schemas.review import Review
from app.repositories.movie_repo import load_all as load_movies
from app.repositories.review_repo import load_all as load_reviews


def _build_idx_to_uuid(movies: List[Dict]) -> Dict[int, str]:
    return {
        idx + 1: mv.get("id")
        for idx, mv in enumerate(movies)
        if isinstance(mv.get("id"), str)
    }


def _normalize_review_movie_id(
    rv: Dict,
    idx_to_uuid: Dict[int, str],
) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Normalize a review's movieId to a UUID string.

    Returns (uuid_or_none, maybe_modified_review_dict_or_none).
    If the id cannot be resolved, returns (None, None).
    """
    movie_id = rv.get("movieId")
    if isinstance(movie_id, str):
        return movie_id, rv
    if isinstance(movie_id, int):
        uuid = idx_to_uuid.get(movie_id)
        if not uuid:
            return None, None
        return uuid, {**rv, "movieId": uuid}
    return None, None

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

    idx_to_uuid = _build_idx_to_uuid(movies)

    start = (page - 1) * per_page
    taken = 0
    seen = 0
    results: List[Review] = []

    for rv in load_reviews():
        uuid, normalized = _normalize_review_movie_id(rv, idx_to_uuid)
        if uuid is None or normalized is None:
            continue
        if uuid not in matched_movie_ids:
            continue
        if seen < start:
            seen += 1
            continue
        results.append(Review(**normalized))
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

    idx_to_uuid = _build_idx_to_uuid(movies)

    results: List[Review] = []
    for rv in load_reviews():
        uuid, normalized = _normalize_review_movie_id(rv, idx_to_uuid)
        if uuid is None or normalized is None:
            continue
        if uuid not in matched_movie_ids:
            continue
        results.append(Review(**normalized))
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

    idx_to_uuid = _build_idx_to_uuid(movies)

    buckets: Dict[str, List[Review]] = {mid: [] for mid in matched_ids}
    for rv in load_reviews():
        uuid, normalized = _normalize_review_movie_id(rv, idx_to_uuid)
        if uuid is None or normalized is None:
            continue
        if uuid in matched_ids:
            try:
                buckets[uuid].append(Review(**normalized))
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
