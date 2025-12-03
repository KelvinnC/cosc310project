from typing import Dict, List, Set, Optional

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


def _legacy_index_to_id_map() -> Dict[int, str]:
    """Map 1-based legacy integer indices to movie UUID ids.

    Some historic data stored integer movieId values corresponding to the
    position of the movie in the movies list (1-based). Build a mapping so
    that those legacy values can be resolved to their string ids.
    """
    mapping: Dict[int, str] = {}
    for idx, mv in enumerate(load_movies(), start=1):
        mid = mv.get("id")
        if isinstance(mid, str):
            mapping[idx] = mid
    return mapping


def _resolve_movie_id(raw_id: object, legacy_map: Dict[int, str]) -> Optional[str]:
    """Resolve a raw movieId (str or legacy int) to a string id.

    Returns the resolved string id if possible, otherwise None.
    """
    if isinstance(raw_id, str):
        return raw_id
    if isinstance(raw_id, int):
        return legacy_map.get(raw_id)
    return None


def _iter_matching_reviews(search: MovieSearch, *, page: int, per_page: int) -> List[Review]:
    matched_movie_ids = _matching_movie_ids(search)
    if not matched_movie_ids:
        return []

    legacy_map = _legacy_index_to_id_map()
    start = (page - 1) * per_page
    taken = 0
    seen = 0
    results: List[Review] = []

    for rv in load_reviews():
        resolved = _resolve_movie_id(rv.get("movieId"), legacy_map)
        if resolved is None or resolved not in matched_movie_ids:
            continue
        if seen < start:
            seen += 1
            continue
        rv_copy = dict(rv)
        rv_copy["movieId"] = resolved
        results.append(Review(**rv_copy))
        taken += 1
        seen += 1
        if taken >= per_page:
            return results
    return results


def all_matching_reviews(search: MovieSearch) -> List[Review]:
    matched_movie_ids = _matching_movie_ids(search)
    if not matched_movie_ids:
        return []

    legacy_map = _legacy_index_to_id_map()
    results: List[Review] = []
    for rv in load_reviews():
        resolved = _resolve_movie_id(rv.get("movieId"), legacy_map)
        if resolved is None or resolved not in matched_movie_ids:
            continue
        rv_copy = dict(rv)
        rv_copy["movieId"] = resolved
        results.append(Review(**rv_copy))
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

    legacy_map = _legacy_index_to_id_map()
    buckets: Dict[str, List[Review]] = {mid: [] for mid in matched_ids}
    for rv in load_reviews():
        resolved = _resolve_movie_id(rv.get("movieId"), legacy_map)
        if resolved is None or resolved not in matched_ids:
            continue
        try:
            rv_copy = dict(rv)
            rv_copy["movieId"] = resolved
            buckets[resolved].append(Review(**rv_copy))
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
