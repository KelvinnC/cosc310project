from pathlib import Path
from typing import Any, Dict, List, Optional
import json, os

from app.repositories import movie_repo

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "reviews.json"


def load_all(load_invisible: bool = False) -> List[Dict[str, Any]]:
    """Loads reviews from reviews.json.

    If the output is user-facing, invisible reviews should not be loaded.
    Hidden reviews should be loaded in cases of subsequent save_all calls
    to prevent overwriting of data.
    """
    if not DATA_PATH.exists():
        return []
    with DATA_PATH.open("r", encoding="utf-8-sig") as f:
        result = json.load(f)
        if load_invisible:
            return result
        return [review for review in result if review.get("visible", True)]


def _to_float(val: Any) -> Optional[float]:
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def get_all_reviews(
    *,
    rating: Optional[float] = None,
    sort_by: Optional[str] = None,
    order: str = "asc",
) -> List[Dict[str, Any]]:
    """
    Filtering: if `rating` is provided, include only reviews whose rating equals
    this value. Non-numeric ratings wont match.

    Sorting: `sort_by` supports 'rating', 'movieId', or 'movieTitle'
    with `order` controlling ascending or descending. Movie-based sorts
    use string UUID `movieId`; legacy integer index handling has been removed.
    """
    reviews = load_all()
    result: List[Dict[str, Any]] = list(reviews)

    if rating is not None:
        target = _to_float(rating)
        result = [rv for rv in result if _to_float(rv.get("rating")) == target]

    if not sort_by:
        return result

    key = (sort_by or "").lower()
    reverse = (order or "asc").lower() == "desc"

    if key == "rating":
        def _rating_key(rv: Dict[str, Any]):
            val = _to_float(rv.get("rating"))
            if val is None:
                return (0, 0.0)
            return (1, val if not reverse else -val)

        return sorted(result, key=_rating_key)

    if key in ("movieid", "movietitle"):
        movies = movie_repo.load_all()

        if key == "movieid":
            def _movie_id_key(rv: Dict[str, Any]):
                mid = rv.get("movieId")
                if not isinstance(mid, str):
                    return (0, "")
                return (1, mid)

            return sorted(result, key=_movie_id_key, reverse=reverse)

        id_to_title: Dict[str, str] = {}
        for mv in movies:
            mid = mv.get("id")
            title = mv.get("title") or ""
            if isinstance(mid, str):
                id_to_title[mid] = title

        def _movie_title_key(rv: Dict[str, Any]):
            mid = rv.get("movieId")
            if not isinstance(mid, str):
                return (0, "")
            return (1, id_to_title.get(mid, ""))

        return sorted(result, key=_movie_title_key, reverse=reverse)

    return result


def save_all(reviews: List[Dict[str, Any]]) -> None:
    tmp = DATA_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8-sig") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_PATH)
