import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_search_movies_with_reviews_uuid_ids(mocker, client):
    movies = [
        {"id": "uuid-joker", "title": "Joker", "description": "", "duration": 120, "genre": "Drama", "release": "2019-10-04"},
        {"id": "uuid-inception", "title": "Inception", "description": "", "duration": 148, "genre": "Sci-Fi", "release": "2010-07-16"},
    ]
    reviews = [
        {"id": 10, "movieId": "uuid-inception", "date": "2020-01-01", "authorId": 1, "reviewTitle": "Great!", "reviewBody": "Loved the layers", "rating": 5.0, "votes": 0, "flagged": False},
        {"id": 11, "movieId": "uuid-inception", "date": "2020-01-02", "authorId": 1, "reviewTitle": "Mind-bending", "reviewBody": "Dreams within dreams", "rating": 4.5, "votes": 0, "flagged": False},
        {"id": 12, "movieId": "uuid-joker", "date": "2020-01-03", "authorId": 2, "reviewTitle": "Intense", "reviewBody": "Dark character study", "rating": 4.0, "votes": 0, "flagged": False},
    ]
    mocker.patch("app.services.search_service.load_movies", return_value=movies)
    mocker.patch("app.services.search_service.load_reviews", return_value=reviews)

    resp = client.get("/reviews/search", params={"title": "Incep"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    mv = data[0]
    assert mv["id"] == "uuid-inception"
    assert mv["title"] == "Inception"
    assert isinstance(mv.get("reviews"), list)
    assert {r["id"] for r in mv["reviews"]} == {10, 11}


def test_search_movies_with_reviews_legacy_integer_ids(mocker, client):
    movies = [
        {"id": "uuid-joker", "title": "Joker", "description": "", "duration": 120, "genre": "Drama", "release": "2019-10-04"},
        {"id": "uuid-inception", "title": "Inception", "description": "", "duration": 148, "genre": "Sci-Fi", "release": "2010-07-16"},
    ]
    reviews = [
        {"id": 10, "movieId": "uuid-inception", "date": "2020-01-01", "authorId": 1, "reviewTitle": "Great!", "reviewBody": "Loved the layers", "rating": 5.0, "votes": 0, "flagged": False},
        {"id": 12, "movieId": "uuid-joker", "date": "2020-01-03", "authorId": 2, "reviewTitle": "Intense", "reviewBody": "Dark character study", "rating": 4.0, "votes": 0, "flagged": False},
    ]
    mocker.patch("app.services.search_service.load_movies", return_value=movies)
    mocker.patch("app.services.search_service.load_reviews", return_value=reviews)

    resp = client.get("/reviews/search", params={"title": "incePtion"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    mv = data[0]
    assert mv["id"] == "uuid-inception"
    assert len(mv["reviews"]) == 1
    assert mv["reviews"][0]["reviewTitle"] == "Great!"


def test_search_movies_with_reviews_no_match_returns_empty(mocker, client):
    mocker.patch("app.services.search_service.load_movies", return_value=[{"id": "uuid-joker", "title": "Joker", "description": "", "duration": 120, "genre": "Drama", "release": "2019-10-04"}])
    mocker.patch("app.services.search_service.load_reviews", return_value=[{"id": 99, "movieId": "uuid-joker", "date": "2020-01-01", "authorId": 1, "reviewTitle": "ok", "reviewBody": "ok", "rating": 5.0, "votes": 0, "flagged": False}])

    resp = client.get("/reviews/search", params={"title": "Nonexistent"})
    assert resp.status_code == 200
    assert resp.json() == []
