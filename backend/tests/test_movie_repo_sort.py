import pytest
from app.repositories.movie_repo import get_all_movies


def test_get_all_movies_returns_copy_when_no_sort(mocker):
    data = [
        {"id": "1", "title": "A", "rating": 7.5},
        {"id": "2", "title": "B", "rating": 9.0},
    ]
    mocker.patch("app.repositories.movie_repo.load_all", return_value=data)
    result = get_all_movies()
    assert result == data
    assert result is not data


def test_sort_by_rating_ascending(mocker):
    data = [
        {"id": "1", "title": "A", "rating": 7.5},
        {"id": "2", "title": "B", "rating": 9.0},
        {"id": "3", "title": "C", "rating": 5.0},
    ]
    mocker.patch("app.repositories.movie_repo.load_all", return_value=data)
    result = get_all_movies(sort_by="rating", order="asc")
    assert [m["id"] for m in result] == ["3", "1", "2"]
    assert data == [
        {"id": "1", "title": "A", "rating": 7.5},
        {"id": "2", "title": "B", "rating": 9.0},
        {"id": "3", "title": "C", "rating": 5.0},
    ]


def test_sort_by_rating_descending(mocker):
    data = [
        {"id": "1", "title": "A", "rating": 7.5},
        {"id": "2", "title": "B", "rating": 9.0},
        {"id": "3", "title": "C", "rating": 5.0},
    ]
    mocker.patch("app.repositories.movie_repo.load_all", return_value=data)
    result = get_all_movies(sort_by="rating", order="desc")
    assert [m["id"] for m in result] == ["2", "1", "3"]


def test_sort_by_rating_handles_strings_and_missing(mocker):
    data = [
        {"id": "1", "title": "A", "rating": "8.0"},
        {"id": "2", "title": "B"},
        {"id": "3", "title": "C", "rating": 6.0},
    ]
    mocker.patch("app.repositories.movie_repo.load_all", return_value=data)

    asc = get_all_movies(sort_by="rating", order="asc")
    assert [m["id"] for m in asc] == ["2", "3", "1"]

    desc = get_all_movies(sort_by="rating", order="desc")
    assert [m["id"] for m in desc] == ["2", "1", "3"]

