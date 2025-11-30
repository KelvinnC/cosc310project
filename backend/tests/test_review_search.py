import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.review_service import list_reviews_paginated


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# Service layer tests

def test_search_by_review_title(mocker):
    reviews = [
        {"id": 1, "movieId": "A", "authorId": 1, "rating": 5, "reviewTitle": "Amazing Film", "reviewBody": "Great movie", "date": "2020-01-01", "visible": True},
        {"id": 2, "movieId": "B", "authorId": 2, "rating": 4, "reviewTitle": "Good Movie", "reviewBody": "Enjoyed it", "date": "2020-01-02", "visible": True},
        {"id": 3, "movieId": "C", "authorId": 3, "rating": 3, "reviewTitle": "Average", "reviewBody": "It was okay", "date": "2020-01-03", "visible": True},
    ]
    movies = [
        {"id": "A", "title": "The Matrix"},
        {"id": "B", "title": "Inception"},
        {"id": "C", "title": "Avatar"},
    ]
    mocker.patch("app.services.review_service.load_all", return_value=reviews)
    mocker.patch("app.repositories.movie_repo.load_all", return_value=movies)

    result = list_reviews_paginated(search="Amazing")
    assert result.total == 1
    assert result.reviews[0].id == 1


def test_search_by_review_body(mocker):
    reviews = [
        {"id": 1, "movieId": "A", "authorId": 1, "rating": 5, "reviewTitle": "Title One", "reviewBody": "This movie was incredible", "date": "2020-01-01", "visible": True},
        {"id": 2, "movieId": "B", "authorId": 2, "rating": 4, "reviewTitle": "Title Two", "reviewBody": "Loved every moment", "date": "2020-01-02", "visible": True},
        {"id": 3, "movieId": "C", "authorId": 3, "rating": 3, "reviewTitle": "Title Three", "reviewBody": "It was just okay", "date": "2020-01-03", "visible": True},
    ]
    movies = [
        {"id": "A", "title": "The Matrix"},
        {"id": "B", "title": "Inception"},
        {"id": "C", "title": "Avatar"},
    ]
    mocker.patch("app.services.review_service.load_all", return_value=reviews)
    mocker.patch("app.repositories.movie_repo.load_all", return_value=movies)

    result = list_reviews_paginated(search="incredible")
    assert result.total == 1
    assert result.reviews[0].id == 1


def test_search_by_movie_title(mocker):
    reviews = [
        {"id": 1, "movieId": "A", "authorId": 1, "rating": 5, "reviewTitle": "Great", "reviewBody": "Loved it", "date": "2020-01-01", "visible": True},
        {"id": 2, "movieId": "B", "authorId": 2, "rating": 4, "reviewTitle": "Good", "reviewBody": "Nice film", "date": "2020-01-02", "visible": True},
        {"id": 3, "movieId": "C", "authorId": 3, "rating": 3, "reviewTitle": "Okay", "reviewBody": "Average", "date": "2020-01-03", "visible": True},
    ]
    movies = [
        {"id": "A", "title": "The Matrix"},
        {"id": "B", "title": "Inception"},
        {"id": "C", "title": "Avatar"},
    ]
    mocker.patch("app.services.review_service.load_all", return_value=reviews)
    mocker.patch("app.repositories.movie_repo.load_all", return_value=movies)

    result = list_reviews_paginated(search="Matrix")
    assert result.total == 1
    assert result.reviews[0].id == 1
    assert result.reviews[0].movieTitle == "The Matrix"


def test_search_case_insensitive(mocker):
    reviews = [
        {"id": 1, "movieId": "A", "authorId": 1, "rating": 5, "reviewTitle": "AMAZING", "reviewBody": "Great", "date": "2020-01-01", "visible": True},
        {"id": 2, "movieId": "B", "authorId": 2, "rating": 4, "reviewTitle": "Good", "reviewBody": "Nice", "date": "2020-01-02", "visible": True},
    ]
    movies = [
        {"id": "A", "title": "The Matrix"},
        {"id": "B", "title": "Inception"},
    ]
    mocker.patch("app.services.review_service.load_all", return_value=reviews)
    mocker.patch("app.repositories.movie_repo.load_all", return_value=movies)

    result = list_reviews_paginated(search="amazing")
    assert result.total == 1
    assert result.reviews[0].id == 1


def test_search_multiple_matches(mocker):
    reviews = [
        {"id": 1, "movieId": "A", "authorId": 1, "rating": 5, "reviewTitle": "Great movie", "reviewBody": "Loved it", "date": "2020-01-01", "visible": True},
        {"id": 2, "movieId": "B", "authorId": 2, "rating": 4, "reviewTitle": "Good", "reviewBody": "Great film", "date": "2020-01-02", "visible": True},
        {"id": 3, "movieId": "C", "authorId": 3, "rating": 3, "reviewTitle": "Okay", "reviewBody": "Average", "date": "2020-01-03", "visible": True},
    ]
    movies = [
        {"id": "A", "title": "The Matrix"},
        {"id": "B", "title": "Inception"},
        {"id": "C", "title": "Avatar"},
    ]
    mocker.patch("app.services.review_service.load_all", return_value=reviews)
    mocker.patch("app.repositories.movie_repo.load_all", return_value=movies)

    result = list_reviews_paginated(search="great")
    assert result.total == 2
    ids = [r.id for r in result.reviews]
    assert 1 in ids
    assert 2 in ids


def test_search_no_matches(mocker):
    reviews = [
        {"id": 1, "movieId": "A", "authorId": 1, "rating": 5, "reviewTitle": "Great", "reviewBody": "Loved it", "date": "2020-01-01", "visible": True},
        {"id": 2, "movieId": "B", "authorId": 2, "rating": 4, "reviewTitle": "Good", "reviewBody": "Nice", "date": "2020-01-02", "visible": True},
    ]
    movies = [
        {"id": "A", "title": "The Matrix"},
        {"id": "B", "title": "Inception"},
    ]
    mocker.patch("app.services.review_service.load_all", return_value=reviews)
    mocker.patch("app.repositories.movie_repo.load_all", return_value=movies)

    result = list_reviews_paginated(search="nonexistent")
    assert result.total == 0
    assert result.reviews == []


def test_search_empty_string_returns_all(mocker):
    reviews = [
        {"id": 1, "movieId": "A", "authorId": 1, "rating": 5, "reviewTitle": "Great", "reviewBody": "Loved it", "date": "2020-01-01", "visible": True},
        {"id": 2, "movieId": "B", "authorId": 2, "rating": 4, "reviewTitle": "Good", "reviewBody": "Nice", "date": "2020-01-02", "visible": True},
    ]
    movies = [
        {"id": "A", "title": "The Matrix"},
        {"id": "B", "title": "Inception"},
    ]
    mocker.patch("app.services.review_service.load_all", return_value=reviews)
    mocker.patch("app.repositories.movie_repo.load_all", return_value=movies)

    result = list_reviews_paginated(search="")
    assert result.total == 2


def test_search_with_pagination(mocker):
    # Create 10 reviews that match search, test pagination
    reviews = [
        {"id": i, "movieId": "A", "authorId": 1, "rating": 5, "reviewTitle": f"Great Review {i}", "reviewBody": "Body", "date": "2020-01-01", "visible": True}
        for i in range(1, 11)
    ]
    movies = [{"id": "A", "title": "The Matrix"}]
    mocker.patch("app.services.review_service.load_all", return_value=reviews)
    mocker.patch("app.repositories.movie_repo.load_all", return_value=movies)

    result = list_reviews_paginated(search="Great", per_page=3, page=1)
    assert result.total == 10
    assert result.total_pages == 4
    assert len(result.reviews) == 3
    assert result.page == 1

    result2 = list_reviews_paginated(search="Great", per_page=3, page=2)
    assert len(result2.reviews) == 3
    assert result2.page == 2


def test_search_combined_with_rating_filter(mocker):
    reviews = [
        {"id": 1, "movieId": "A", "authorId": 1, "rating": 5, "reviewTitle": "Great", "reviewBody": "Loved it", "date": "2020-01-01", "visible": True},
        {"id": 2, "movieId": "B", "authorId": 2, "rating": 3, "reviewTitle": "Great", "reviewBody": "It was okay", "date": "2020-01-02", "visible": True},
        {"id": 3, "movieId": "C", "authorId": 3, "rating": 5, "reviewTitle": "Bad", "reviewBody": "Hated it", "date": "2020-01-03", "visible": True},
    ]
    movies = [
        {"id": "A", "title": "The Matrix"},
        {"id": "B", "title": "Inception"},
        {"id": "C", "title": "Avatar"},
    ]
    mocker.patch("app.services.review_service.load_all", return_value=reviews)
    mocker.patch("app.repositories.movie_repo.load_all", return_value=movies)

    result = list_reviews_paginated(search="Great", rating=5)
    assert result.total == 1
    assert result.reviews[0].id == 1


# Endpoint tests

def test_search_endpoint_basic(mocker, client):
    reviews = [
        {"id": 1, "movieId": "A", "authorId": 1, "rating": 5, "reviewTitle": "Amazing Film", "reviewBody": "Great", "flagged": False, "votes": 0, "date": "2020-01-01", "visible": True},
        {"id": 2, "movieId": "B", "authorId": 2, "rating": 4, "reviewTitle": "Good Movie", "reviewBody": "Nice", "flagged": False, "votes": 0, "date": "2020-01-02", "visible": True},
    ]
    movies = [
        {"id": "A", "title": "The Matrix"},
        {"id": "B", "title": "Inception"},
    ]
    mocker.patch("app.services.review_service.load_all", return_value=reviews)
    mocker.patch("app.repositories.movie_repo.load_all", return_value=movies)

    resp = client.get("/reviews", params={"search": "Amazing"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["reviews"][0]["id"] == 1


def test_search_endpoint_movie_title(mocker, client):
    reviews = [
        {"id": 1, "movieId": "A", "authorId": 1, "rating": 5, "reviewTitle": "Great", "reviewBody": "Good", "flagged": False, "votes": 0, "date": "2020-01-01", "visible": True},
        {"id": 2, "movieId": "B", "authorId": 2, "rating": 4, "reviewTitle": "Nice", "reviewBody": "Fun", "flagged": False, "votes": 0, "date": "2020-01-02", "visible": True},
    ]
    movies = [
        {"id": "A", "title": "The Matrix"},
        {"id": "B", "title": "Inception"},
    ]
    mocker.patch("app.services.review_service.load_all", return_value=reviews)
    mocker.patch("app.repositories.movie_repo.load_all", return_value=movies)

    resp = client.get("/reviews", params={"search": "Inception"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["reviews"][0]["movieTitle"] == "Inception"


def test_search_endpoint_with_sort(mocker, client):
    reviews = [
        {"id": 1, "movieId": "A", "authorId": 1, "rating": 3, "reviewTitle": "Great Review", "reviewBody": "Body", "flagged": False, "votes": 0, "date": "2020-01-01", "visible": True},
        {"id": 2, "movieId": "B", "authorId": 2, "rating": 5, "reviewTitle": "Great Film", "reviewBody": "Body", "flagged": False, "votes": 0, "date": "2020-01-02", "visible": True},
        {"id": 3, "movieId": "C", "authorId": 3, "rating": 4, "reviewTitle": "Great Movie", "reviewBody": "Body", "flagged": False, "votes": 0, "date": "2020-01-03", "visible": True},
    ]
    movies = [
        {"id": "A", "title": "Alpha"},
        {"id": "B", "title": "Beta"},
        {"id": "C", "title": "Gamma"},
    ]
    mocker.patch("app.services.review_service.load_all", return_value=reviews)
    mocker.patch("app.repositories.movie_repo.load_all", return_value=movies)

    resp = client.get("/reviews", params={"search": "Great", "sort_by": "rating", "order": "desc"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert [r["id"] for r in data["reviews"]] == [2, 3, 1]
