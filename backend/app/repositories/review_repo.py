from pathlib import Path
import json
from typing import List, Dict, Any

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "reviews.json"


def load_all() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

