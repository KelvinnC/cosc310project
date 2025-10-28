from pathlib import Path
import json
from typing import Dict, Any, List

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "reviews.json"


def load_all() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    with DATA_PATH.open("r", encoding="utf-8-sig") as f:
        return json.load(f)
