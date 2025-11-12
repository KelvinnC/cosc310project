import json
import os
from datetime import datetime
from typing import List, Dict, Any

DATA_FILE = "app/data/flags.json"


def load_all() -> List[Dict[str, Any]]:
    """Load all flags from storage. Returns empty list if file doesn't exist."""
    if not os.path.exists(DATA_FILE):
        return []
    
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_all(flags: List[Dict[str, Any]]) -> None:
    """Save all flags to storage."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(flags, f, indent=2)
