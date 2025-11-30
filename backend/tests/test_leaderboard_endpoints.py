import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_leaderboard_returns_reviews_from_service(mocker, client):
    """Leaderboard endpoint should return reviews provided by the service."""
    from app.schemas.review import Review

    reviews = [
        Review(
            id=1,
            movieId="movie-1",
            authorId="author-1",
            rating=4.0,
            reviewTitle="Review 1",
            reviewBody="This is a review body long enough for testing purposes.",
            flagged=False,
            votes=5,
            date="2025-11-20",
        ),
        Review(
            id=2,
            movieId="movie-2",
            authorId="author-2",
            rating=3.5,
            reviewTitle="Review 2",
            reviewBody="Another sufficiently long review body for the leaderboard.",
            flagged=False,
            votes=10,
            date="2025-11-21",
        ),
    ]

    mock_get = mocker.patch(
        "app.routers.leaderboard.get_leaderboard_reviews",
        return_value=reviews,
    )

    resp = client.get("/leaderboard")
    assert resp.status_code == 200
    mock_get.assert_called_once_with(limit=10)

    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 2
    returned_ids = {item["id"] for item in data}
    assert returned_ids == {1, 2}


def test_leaderboard_handles_no_reviews(mocker, client):
    """no reviews, leaderboard should return an empty list."""
    mocker.patch(
        "app.routers.leaderboard.get_leaderboard_reviews",
        return_value=[],
    )

    resp = client.get("/leaderboard")
    assert resp.status_code == 200
    assert resp.json() == []
