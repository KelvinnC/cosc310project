import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_post_review_requires_authentication(client):
    """POST /reviews without JWT should return 401."""
    payload = {
        "movieId": "UUID-movie-1234",
        "reviewTitle": "unauthorized review",
        "reviewBody": (
            "This is a valid length review body so that payload "
            "passes validation but should still be unauthorized."
        ),
        "rating": 4.0,
        "votes": 0,
        "flagged": False,
    }

    response = client.post("/reviews", json=payload)

    assert response.status_code == 401
    assert "Access Token" in response.json()["detail"]


def test_get_review_by_id_service_404_propagates(mocker, client):
    """HTTPException 404 from get_review_by_id propagates correctly."""
    mocker.patch(
        "app.routers.reviews.get_review_by_id",
        side_effect=HTTPException(status_code=404, detail="Review not found"),
    )

    resp = client.get("/reviews/1")

    assert resp.status_code == 404
    assert "Review not found" in resp.json()["detail"]


def test_get_author_reviews_404_returns_empty_list(mocker, client):
    """HTTP 404 in service should return 200 with empty list."""
    mocker.patch(
        "app.routers.reviews.get_reviews_by_author",
        side_effect=HTTPException(status_code=404, detail="author not found"),
    )

    resp = client.get("/reviews/author/missing-author")

    assert resp.status_code == 200
    assert resp.json() == []


def test_get_author_reviews_non_404_http_error_propagates(mocker, client):
    """Non-404 HTTPException from service should propagate."""
    mocker.patch(
        "app.routers.reviews.get_reviews_by_author",
        side_effect=HTTPException(status_code=500, detail="db error"),
    )

    resp = client.get("/reviews/author/broken-author")

    assert resp.status_code == 500
    assert resp.json()["detail"] == "db error"
