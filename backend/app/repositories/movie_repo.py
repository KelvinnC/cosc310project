from pathlib import Path
import json, os
from typing import List, Dict, Any

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
    """Return all movies, optionally sorted
    - Supports sorting by the "rating" field
    - Sorting direction controlled by `order`
    - Does not mutate the original dataset; returns a new list
    """
    movies = load_all()
    movies_copy: List[Dict[str, Any]] = list(movies)

    if not sort_by:
        return movies_copy

    direction = (order or "asc").lower()
    reverse = True if direction == "desc" else False

    if sort_by == "rating":
        def _rating_key(m: Dict[str, Any]):
            val = m.get("rating")
            try:
                return float(val)
            except (TypeError, ValueError):
                return float("-inf") if not reverse else float("inf")

        return sorted(movies_copy, key=_rating_key, reverse=reverse)

    return movies_copy
