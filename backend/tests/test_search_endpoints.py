import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_search_reviews_partial_case_insensitive_uuid_ids(mocker, client):
    movies = [
        {"id": "uuid-joker", "title": "Joker", "description": "", "duration": 120, "genre": "Drama", "release": "2019-10-04"},
        {"id": "uuid-inception", "title": "Inception", "description": "", "duration": 148, "genre": "Sci-Fi", "release": "2010-07-16"},
    ]
    reviews = [
        {"id": 10, "movieId": "uuid-inception", "date": "2020-01-01", "authorId": 1, "reviewTitle": "Great!", "reviewBody": "Loved the layers", "rating": 9.0, "votes": 0, "flagged": False},
        {"id": 11, "movieId": "uuid-inception", "date": "2020-01-02", "authorId": 1, "reviewTitle": "Mind-bending", "reviewBody": "Dreams within dreams", "rating": 8.5, "votes": 0, "flagged": False},
        {"id": 12, "movieId": "uuid-joker", "date": "2020-01-03", "authorId": 2, "reviewTitle": "Intense", "reviewBody": "Dark character study", "rating": 8.0, "votes": 0, "flagged": False},
    ]
    mocker.patch("app.services.search_service.load_movies", return_value=movies)
    pages = [
        [
            {"id": 12, "movieId": "uuid-joker", "date": "2020-01-03", "authorId": 2, "reviewTitle": "Intense", "reviewBody": "Dark character study", "rating": 8.0, "votes": 0, "flagged": False},
        ],
        [
            {"id": 10, "movieId": "uuid-inception", "date": "2020-01-01", "authorId": 1, "reviewTitle": "Great!", "reviewBody": "Loved the layers", "rating": 9.0, "votes": 0, "flagged": False},
            {"id": 11, "movieId": "uuid-inception", "date": "2020-01-02", "authorId": 1, "reviewTitle": "Mind-bending", "reviewBody": "Dreams within dreams", "rating": 8.5, "votes": 0, "flagged": False},
        ],
    ]
    mocker.patch("app.services.search_service.iter_pages", return_value=iter(pages))

    resp = client.get("/reviews/search", params={"title": "Incep"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert all(r["movieId"] == "uuid-inception" for r in data)


def test_search_reviews_legacy_integer_ids_still_match(mocker, client):
    movies = [
        {"id": "uuid-joker", "title": "Joker", "description": "", "duration": 120, "genre": "Drama", "release": "2019-10-04"},
        {"id": "uuid-inception", "title": "Inception", "description": "", "duration": 148, "genre": "Sci-Fi", "release": "2010-07-16"},
    ]
    reviews = [
        {"id": 10, "movieId": 2, "date": "2020-01-01", "authorId": 1, "reviewTitle": "Great!", "reviewBody": "Loved the layers", "rating": 9.0, "votes": 0, "flagged": False},
        {"id": 12, "movieId": 1, "date": "2020-01-03", "authorId": 2, "reviewTitle": "Intense", "reviewBody": "Dark character study", "rating": 8.0, "votes": 0, "flagged": False},
    ]
    mocker.patch("app.services.search_service.load_movies", return_value=movies)
    pages = [
        [
            {"id": 12, "movieId": 1, "date": "2020-01-03", "authorId": 2, "reviewTitle": "Intense", "reviewBody": "Dark character study", "rating": 8.0, "votes": 0, "flagged": False},
        ],
        [
            {"id": 10, "movieId": 2, "date": "2020-01-01", "authorId": 1, "reviewTitle": "Great!", "reviewBody": "Loved the layers", "rating": 9.0, "votes": 0, "flagged": False},
        ],
    ]
    mocker.patch("app.services.search_service.iter_pages", return_value=iter(pages))

    resp = client.get("/reviews/search", params={"title": "incePtion"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["reviewTitle"] == "Great!"


def test_search_reviews_no_match_returns_empty(mocker, client):
    mocker.patch("app.services.search_service.load_movies", return_value=[{"id": "uuid-joker", "title": "Joker", "description": "", "duration": 120, "genre": "Drama", "release": "2019-10-04"}])
    mocker.patch("app.services.search_service.iter_pages", return_value=iter([[{"id": 99, "movieId": "uuid-joker", "date": "2020-01-01", "authorId": 1, "reviewTitle": "ok", "reviewBody": "ok", "rating": 5.0, "votes": 0, "flagged": False}]]))

    resp = client.get("/reviews/search", params={"title": "Nonexistent"})
    assert resp.status_code == 200
    assert resp.json() == []

