import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_leaderboard_returns_reviews_and_movies(mocker, client):
    """Leaderboard endpoint should return reviews and movies provided by the service."""
    from app.schemas.review import Review
    from app.schemas.movie import Movie

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

    movies = [
    Movie(
        id="movie-1",
        title="Movie 1",
        year=2025,
        genre="Drama",
        description="A dramatic test movie.",
        duration=120,
        release="2025-11-20",
        rating=1
    ),
    Movie(
        id="movie-2",
        title="Movie 2",
        year=2025,
        genre="Comedy",
        description="A comedic test movie.",
        duration=95,
        release="2025-11-21",
        rating=2
    ),
]

    mock_reviews = mocker.patch(
        "app.routers.leaderboard.get_leaderboard_reviews",
        return_value=reviews,
    )
    mock_movies = mocker.patch(
        "app.routers.leaderboard.get_leaderboard_movies",
        return_value=movies,
    )

    resp = client.get("/leaderboard")
    assert resp.status_code == 200
    mock_reviews.assert_called_once_with(limit=10)
    mock_movies.assert_called_once_with(limit=10)

    data = resp.json()

    assert "reviews" in data
    assert "movies" in data

    assert isinstance(data["reviews"], list)
    returned_review_ids = {item["id"] for item in data["reviews"]}
    assert returned_review_ids == {1, 2}

    assert isinstance(data["movies"], list)
    returned_movie_ids = {item["id"] for item in data["movies"]}
    assert returned_movie_ids == {"movie-1", "movie-2"}


def test_leaderboard_handles_no_reviews_no_movies(mocker, client):
    """No reviews, leaderboard should return an empty reviews list and movies from the service."""
    from app.schemas.movie import Movie

    mocker.patch(
        "app.routers.leaderboard.get_leaderboard_reviews",
        return_value=[],
    )

    mocker.patch(
        "app.routers.leaderboard.get_leaderboard_movies",
        return_value=[]
    )

    resp = client.get("/leaderboard")
    assert resp.status_code == 200
    assert resp.json() == {'movies': [], 'reviews': []}
