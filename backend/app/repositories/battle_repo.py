# battle_repo.py
from pathlib import Path
import json, os
from typing import List, Dict, Any

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "battles.json"


def load_all() -> List[Dict[str, Any]]:
    """Load all battles from battles.json"""
    if not DATA_PATH.exists():
        return []
    try:
        with DATA_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def get_by_id(battle_id: str) -> Dict[str, Any] | None:
    """Load a specific battle by ID"""
    battles = load_all()
    for battle in battles:
        if battle.get("id") == battle_id:
            return battle
    return None

def save_all(battles: List[Dict[str, Any]]) -> None:
    """Save all battles to battles.json safely using a temp file"""
    tmp = DATA_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(battles, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_PATH)
