from pathlib import Path
import json, os
from typing import Dict, Any, List

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


def save_all(reviews: List[Dict[str, Any]]) -> None:
    tmp = DATA_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8-sig") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_PATH)

