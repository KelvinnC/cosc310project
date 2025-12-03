import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_sort_movies_ascending(mocker, client):
    mocker.patch(
        "app.repositories.movie_repo.load_all",
        return_value=[
            {"id": "1", "title": "A", "rating": 7.5, "genre": "G", "release": "2022-01-01", "description": "d", "duration": 90},
            {"id": "2", "title": "B", "rating": 9.0, "genre": "G", "release": "2022-01-01", "description": "d", "duration": 90},
            {"id": "3", "title": "C", "rating": 5.0, "genre": "G", "release": "2022-01-01", "description": "d", "duration": 90},
        ],
    )
    res = client.get("/movies?sort_by=rating&order=asc")
    assert res.status_code == 200
    data = res.json()
    assert [m["id"] for m in data] == ["3", "1", "2"]


def test_sort_movies_descending(mocker, client):
    mocker.patch(
        "app.repositories.movie_repo.load_all",
        return_value=[
            {"id": "1", "title": "A", "rating": 7.5, "genre": "G", "release": "2022-01-01", "description": "d", "duration": 90},
            {"id": "2", "title": "B", "rating": 9.0, "genre": "G", "release": "2022-01-01", "description": "d", "duration": 90},
            {"id": "3", "title": "C", "rating": 5.0, "genre": "G", "release": "2022-01-01", "description": "d", "duration": 90},
        ],
    )
    res = client.get("/movies?sort_by=rating&order=desc")
    assert res.status_code == 200
    data = res.json()
    assert [m["id"] for m in data] == ["2", "1", "3"]


def test_sort_movies_default_order_is_asc(mocker, client):
    mocker.patch(
        "app.repositories.movie_repo.load_all",
        return_value=[
            {"id": "1", "title": "A", "rating": 7.5, "genre": "G", "release": "2022-01-01", "description": "d", "duration": 90},
            {"id": "2", "title": "B", "rating": 9.0, "genre": "G", "release": "2022-01-01", "description": "d", "duration": 90},
            {"id": "3", "title": "C", "rating": 5.0, "genre": "G", "release": "2022-01-01", "description": "d", "duration": 90},
        ],
    )
    res = client.get("/movies?sort_by=rating")
    assert res.status_code == 200
    data = res.json()
    assert [m["id"] for m in data] == ["3", "1", "2"]
