"""Helper functions for searching and manipulating lists."""

from typing import List, Dict, Any, Callable, TypeVar

T = TypeVar('T')

NOT_FOUND = -1 # Constant for "not found" result


def find_index(
    items: List[T],
    predicate: Callable[[T], bool]
) -> int:
    """Find the index of the first item matching the predicate."""
    for i, item in enumerate(items):
        if predicate(item):
            return i
    return NOT_FOUND


def find_dict_by_id(
    items: List[Dict[str, Any]],
    id_key: str,
    id_value: Any
) -> int:
    """Find the index of the first dictionary with a specific ID value."""
    return find_index(items, lambda item: item.get(id_key) == id_value)
