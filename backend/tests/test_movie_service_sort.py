import pytest
from app.services.movie_service import list_movies


def test_list_movies_no_sort_returns_models_and_does_not_mutate(mocker):
    data = [
        {"id": "1", "title": "A", "rating": 7.5, "genre": "G", "release": "2020-01-01", "description": "d", "duration": 90},
        {"id": "2", "title": "B", "rating": 9.0, "genre": "G", "release": "2021-01-01", "description": "d", "duration": 91},
    ]
    mocker.patch("app.repositories.movie_repo.load_all", return_value=data)
    result = list_movies()
    assert [m.id for m in result] == ["1", "2"]
    assert data == [
        {"id": "1", "title": "A", "rating": 7.5, "genre": "G", "release": "2020-01-01", "description": "d", "duration": 90},
        {"id": "2", "title": "B", "rating": 9.0, "genre": "G", "release": "2021-01-01", "description": "d", "duration": 91},
    ]


def test_sort_by_rating_ascending(mocker):
    data = [
        {"id": "1", "title": "A", "rating": 7.5, "genre": "G", "release": "2020-01-01", "description": "d", "duration": 90},
        {"id": "2", "title": "B", "rating": 9.0, "genre": "G", "release": "2021-01-01", "description": "d", "duration": 91},
        {"id": "3", "title": "C", "rating": 5.0, "genre": "G", "release": "2019-01-01", "description": "d", "duration": 89},
    ]
    mocker.patch("app.repositories.movie_repo.load_all", return_value=data)
    result = list_movies(sort_by="rating", order="asc")
    assert [m.id for m in result] == ["3", "1", "2"]
    assert data[0]["rating"] == 7.5 and data[1]["rating"] == 9.0 and data[2]["rating"] == 5.0


def test_sort_by_rating_descending(mocker):
    data = [
        {"id": "1", "title": "A", "rating": 7.5, "genre": "G", "release": "2020-01-01", "description": "d", "duration": 90},
        {"id": "2", "title": "B", "rating": 9.0, "genre": "G", "release": "2021-01-01", "description": "d", "duration": 91},
        {"id": "3", "title": "C", "rating": 5.0, "genre": "G", "release": "2019-01-01", "description": "d", "duration": 89},
    ]
    mocker.patch("app.repositories.movie_repo.load_all", return_value=data)
    result = list_movies(sort_by="rating", order="desc")
    assert [m.id for m in result] == ["2", "1", "3"]


def test_sort_by_rating_handles_strings_and_missing(mocker):
    data = [
        {"id": "1", "title": "A", "rating": "8.0", "genre": "G", "release": "2020-01-01", "description": "d", "duration": 90},
        {"id": "2", "title": "B", "genre": "G", "release": "2021-01-01", "description": "d", "duration": 91},
        {"id": "3", "title": "C", "rating": 6.0, "genre": "G", "release": "2019-01-01", "description": "d", "duration": 89},
    ]
    mocker.patch("app.repositories.movie_repo.load_all", return_value=data)

    asc = list_movies(sort_by="rating", order="asc")
    assert [m.id for m in asc] == ["2", "3", "1"]

    desc = list_movies(sort_by="rating", order="desc")
    assert [m.id for m in desc] == ["2", "1", "3"]

