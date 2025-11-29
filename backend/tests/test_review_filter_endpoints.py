import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_filter_and_sort_by_rating_desc(mocker, client):
    reviews = [
        {"id": 1, "movieId": "A", "authorId": 10, "rating": 5, "reviewTitle": "t1", "reviewBody": "b1", "flagged": False, "votes": 0, "date": "2020-01-01"},
        {"id": 2, "movieId": "B", "authorId": 11, "rating": 3, "reviewTitle": "t2", "reviewBody": "b2", "flagged": False, "votes": 0, "date": "2020-01-02"},
        {"id": 3, "movieId": "C", "authorId": 12, "rating": "5.0", "reviewTitle": "t3", "reviewBody": "b3", "flagged": False, "votes": 0, "date": "2020-01-03"},
        {"id": 4, "movieId": "D", "authorId": 13, "rating": 4, "reviewTitle": "t4", "reviewBody": "b4", "flagged": False, "votes": 0, "date": "2020-01-04"},
        {"id": 5, "movieId": "E", "authorId": 14, "reviewTitle": "t5", "reviewBody": "b5", "flagged": False, "votes": 0, "date": "2020-01-05"},
    ]
    mocker.patch("app.services.review_service.load_all", return_value=reviews)

    resp = client.get("/reviews", params={"rating": 5, "sort_by": "rating", "order": "desc"})
    assert resp.status_code == 200
    data = resp.json()
    # Response is now paginated
    assert [r["id"] for r in data["reviews"]] == [1, 3]


def test_sort_by_movie_title_asc(mocker, client):
    reviews = [
        {"id": 1, "movieId": "A", "authorId": 10, "rating": 3, "reviewTitle": "t1", "reviewBody": "b1", "flagged": False, "votes": 0, "date": "2020-01-01"},
        {"id": 2, "movieId": "2", "authorId": 11, "rating": 4, "reviewTitle": "t2", "reviewBody": "b2", "flagged": False, "votes": 0, "date": "2020-01-02"},
        {"id": 3, "movieId": "C", "authorId": 12, "rating": 5, "reviewTitle": "t3", "reviewBody": "b3", "flagged": False, "votes": 0, "date": "2020-01-03"},
        {"id": 4, "movieId": "99", "authorId": 13, "rating": 2, "reviewTitle": "t4", "reviewBody": "b4", "flagged": False, "votes": 0, "date": "2020-01-04"},
    ]
    movies = [
        {"id": "A", "title": "Zeta"},
        {"id": "B", "title": "Alpha"},
        {"id": "C", "title": "Omega"},
    ]
    mocker.patch("app.services.review_service.load_all", return_value=reviews)
    mocker.patch("app.repositories.movie_repo.load_all", return_value=movies)

    resp = client.get("/reviews", params={"sort_by": "movie", "order": "asc"})
    assert resp.status_code == 200
    data = resp.json()
    # Response is now paginated
    # Sort key puts unknown movies first (0, "") before known movies (1, title)
    # Ascending: Unknown(2,4), Omega(3), Zeta(1)
    assert [r["id"] for r in data["reviews"]] == [2, 4, 3, 1]
