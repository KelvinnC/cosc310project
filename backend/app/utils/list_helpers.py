"""Helper functions for searching and manipulating lists."""

from typing import List, Dict, Any, Callable, TypeVar

T = TypeVar('T')

# Constant for "not found" result
NOT_FOUND = -1


def find_index(
    items: List[T],
    predicate: Callable[[T], bool]
) -> int:
    """
    Find the index of the first item matching the predicate.
    
    Args:
        items: List to search
        predicate: Function that returns True for matching item
        
    Returns:
        Index of first matching item, or NOT_FOUND (-1) if not found
        
    Example:
        >>> items = [{"id": 1}, {"id": 2}, {"id": 3}]
        >>> find_index(items, lambda x: x["id"] == 2)
        1
    """
    for i, item in enumerate(items):
        if predicate(item):
            return i
    return NOT_FOUND


def find_dict_by_id(
    items: List[Dict[str, Any]],
    id_key: str,
    id_value: Any
) -> int:
    """
    Find the index of a dictionary by a specific ID field.
    
    Args:
        items: List of dictionaries to search
        id_key: Key name to search (e.g., "id", "user_id")
        id_value: Value to match
        
    Returns:
        Index of first matching dict, or NOT_FOUND (-1) if not found
        
    Example:
        >>> battles = [{"id": "b1"}, {"id": "b2"}]
        >>> find_dict_by_id(battles, "id", "b2")
        1
    """
    return find_index(items, lambda item: item.get(id_key) == id_value)
