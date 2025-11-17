"""Tests for list helper utilities."""

import pytest
from app.utils.list_helpers import find_index, find_dict_by_id, NOT_FOUND


def test_find_index_finds_matching_item():
    """Test finding item by predicate."""
    items = [1, 2, 3, 4, 5]
    index = find_index(items, lambda x: x == 3)
    assert index == 2


def test_find_index_returns_first_match():
    """Test that find_index returns the first matching item."""
    items = [1, 2, 3, 2, 4]
    index = find_index(items, lambda x: x == 2)
    assert index == 1  # First occurrence


def test_find_index_not_found():
    """Test find_index returns NOT_FOUND when no match."""
    items = [1, 2, 3]
    index = find_index(items, lambda x: x == 99)
    assert index == NOT_FOUND


def test_find_index_empty_list():
    """Test find_index on empty list."""
    items = []
    index = find_index(items, lambda x: x == 1)
    assert index == NOT_FOUND


def test_find_index_complex_predicate():
    """Test find_index with complex predicate."""
    items = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
    index = find_index(items, lambda x: x["age"] > 26)
    assert index == 0


def test_find_dict_by_id_string_id():
    """Test finding dict by string ID."""
    battles = [
        {"id": "battle-1", "winner": "A"},
        {"id": "battle-2", "winner": "B"},
        {"id": "battle-3", "winner": "C"}
    ]
    index = find_dict_by_id(battles, "id", "battle-2")
    assert index == 1


def test_find_dict_by_id_integer_id():
    """Test finding dict by integer ID."""
    reviews = [
        {"id": 1, "title": "Review 1"},
        {"id": 2, "title": "Review 2"},
        {"id": 3, "title": "Review 3"}
    ]
    index = find_dict_by_id(reviews, "id", 2)
    assert index == 1


def test_find_dict_by_id_not_found():
    """Test find_dict_by_id when ID doesn't exist."""
    items = [{"id": 1}, {"id": 2}]
    index = find_dict_by_id(items, "id", 99)
    assert index == NOT_FOUND


def test_find_dict_by_id_missing_key():
    """Test find_dict_by_id when key doesn't exist in dict."""
    items = [{"name": "Alice"}, {"name": "Bob"}]
    index = find_dict_by_id(items, "id", 1)
    assert index == NOT_FOUND


def test_find_dict_by_id_none_value():
    """Test find_dict_by_id searching for None."""
    items = [{"id": None}, {"id": 2}]
    index = find_dict_by_id(items, "id", None)
    assert index == 0


def test_find_dict_by_id_custom_key():
    """Test find_dict_by_id with custom key name."""
    users = [
        {"user_id": "u1", "name": "Alice"},
        {"user_id": "u2", "name": "Bob"}
    ]
    index = find_dict_by_id(users, "user_id", "u2")
    assert index == 1


def test_find_dict_by_id_empty_list():
    """Test find_dict_by_id on empty list."""
    items = []
    index = find_dict_by_id(items, "id", 1)
    assert index == NOT_FOUND


def test_not_found_constant():
    """Test that NOT_FOUND constant is -1."""
    assert NOT_FOUND == -1


def test_find_index_with_all_false_predicate():
    """Test find_index when predicate always returns False."""
    items = [1, 2, 3, 4, 5]
    index = find_index(items, lambda x: False)
    assert index == NOT_FOUND


def test_find_index_with_all_true_predicate():
    """Test find_index when predicate always returns True (returns first)."""
    items = [1, 2, 3]
    index = find_index(items, lambda x: True)
    assert index == 0
