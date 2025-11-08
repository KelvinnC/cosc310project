from pathlib import Path
import json, os
from typing import List, Dict, Any, Optional

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "movies.json"

def load_all() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    with DATA_PATH.open("r", encoding="utf-8-sig") as f:
        return json.load(f)
    
def save_all(movies: List[Dict[str, Any]]) -> None:
    tmp = DATA_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(movies, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_PATH)

def get_all_movies(sort_by: str = None, order: str = "asc") -> List[Dict[str, Any]]:
    """Return all movies, optionally sorted.
    - Supports sorting by the "rating" field.
    - Sorting direction controlled by `order` ("asc" or "desc").
    - Does not mutate the original dataset; returns a new list.
    """
    movies = load_all()
    movies_copy: List[Dict[str, Any]] = list(movies)

    if not sort_by:
        return movies_copy

    direction = (order or "asc").lower()
    reverse = True if direction == "desc" else False

    if sort_by == "rating":
        def _coerce_float(v: Any) -> Optional[float]:
            try:
                return float(v)
            except (TypeError, ValueError):
                return None

        has_any_rating = any(_coerce_float(m.get("rating")) is not None for m in movies_copy)

        derived_ratings: Dict[str, float] = {}
        if not has_any_rating:
            try:
                from app.repositories.review_repo import load_all as load_reviews
                reviews = load_reviews()
                index_to_id = {idx + 1: mv.get("id") for idx, mv in enumerate(movies_copy)}
                totals: Dict[str, float] = {}
                counts: Dict[str, int] = {}
                for rv in reviews:
                    mv_id = rv.get("movieId")
                    rating = _coerce_float(rv.get("rating"))
                    if rating is None:
                        continue
                    if isinstance(mv_id, int):
                        target_id = index_to_id.get(mv_id)
                    else:
                        target_id = str(mv_id) if mv_id is not None else None
                    if not target_id:
                        continue
                    totals[target_id] = totals.get(target_id, 0.0) + rating
                    counts[target_id] = counts.get(target_id, 0) + 1
                for mid, total in totals.items():
                    cnt = counts.get(mid) or 0
                    if cnt > 0:
                        derived_ratings[mid] = total / cnt
            except Exception:
                derived_ratings = {}

        def _rating_key(m: Dict[str, Any]):
            val = _coerce_float(m.get("rating"))
            if val is None:
                val = derived_ratings.get(m.get("id"))
            if val is None:
                return float("-inf") if not reverse else float("inf")
            return val

        return sorted(movies_copy, key=_rating_key, reverse=reverse)

    return movies_copy
