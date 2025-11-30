import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app
from app.middleware.auth_middleware import user_is_author


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def authenticated_client():
    """Client with auth dependency overridden."""
    def mock_user_is_author():
        return {"user_id": "test-user"}
    
    app.dependency_overrides[user_is_author] = mock_user_is_author
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


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


def test_get_review_by_id_internal_error_returns_404(mocker, client):
    """Internal error from get_review_by_id is mapped to 404."""
    mocker.patch(
        "app.routers.reviews.get_review_by_id",
        side_effect=RuntimeError("unexpected failure"),
    )

    resp = client.get("/reviews/1")

    assert resp.status_code == 404
    assert "Review 1 not found" in resp.json()["detail"]


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


def test_put_review_internal_error_returns_404(mocker, authenticated_client):
    """Any exception from update_review should map to 404."""
    mocker.patch(
        "app.routers.reviews.update_review",
        side_effect=Exception("update failed"),
    )

    resp = authenticated_client.put(
        "/reviews/1234",
        json={
            "rating": 3.5,
            "reviewTitle": "missing review",
            "reviewBody": (
                "This review does not exist but the endpoint should "
                "translate the internal error into a not found response."
            ),
            "flagged": False,
            "votes": 0,
            "date": "2022-01-01",
        },
    )

    assert resp.status_code == 404
    assert "Review 1234 not found" in resp.json()["detail"]


def test_delete_review_internal_error_returns_404(mocker, authenticated_client):
    """Any exception from delete_review should map to 404."""
    mocker.patch(
        "app.routers.reviews.delete_review",
        side_effect=Exception("delete failed"),
    )

    resp = authenticated_client.delete("/reviews/9999")

    assert resp.status_code == 404
    assert "Review 9999 not found" in resp.json()["detail"]

