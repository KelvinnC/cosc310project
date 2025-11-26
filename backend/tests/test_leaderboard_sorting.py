import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.review import Review
from app.schemas.movie import Movie

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_endpoint_returns_reviews_and_movies_in_order(mocker, client):
    from app.schemas.review import Review
    from app.schemas.movie import Movie

    reviews = [
        Review(
            id=1,
            movieId="m1",
            authorId="a1",
            rating=4.0,
            reviewTitle="Low votes",
            reviewBody="Body long enough for validation one.",
            flagged=False,
            votes=1,
            date="2025-11-18",
        ),
        Review(
            id=2,
            movieId="m2",
            authorId="a2",
            rating=4.0,
            reviewTitle="High votes",
            reviewBody="Body long enough for validation two.",
            flagged=False,
            votes=10,
            date="2025-11-19",
        ),
        Review(
            id=3,
            movieId="m3",
            authorId="a3",
            rating=4.0,
            reviewTitle="Medium votes",
            reviewBody="Body long enough for validation three.",
            flagged=False,
            votes=5,
            date="2025-11-17",
        ),
    ]

    mocker.patch(
        "app.services.review_service.list_reviews",
        return_value=reviews,
    )

    movies = [
        Movie(
            id="movie-1",
            title="Movie 1",
            year=2025,
            genre="Drama",
            description="A dramatic test movie.",
            duration=120,
            release="2025-11-20",
            rating=5,
        ),
        Movie(
            id="movie-2",
            title="Movie 2",
            year=2025,
            genre="Comedy",
            description="A comedic test movie.",
            duration=95,
            release="2025-11-21",
            rating=2,
        ),
        Movie(
            id="movie-3",
            title="Movie 3",
            year=2023,
            genre="Action",
            description="A test action movie.",
            duration=90,
            release="2025-11-15",
            rating=3,
        ),
    ]

    mocker.patch(
        "app.services.movie_service.list_movies",
        return_value=movies,
    )

    resp = client.get("/leaderboard")
    assert resp.status_code == 200
    data = resp.json()

    votes = [item["votes"] for item in data["reviews"]]
    assert votes == sorted(votes, reverse=True)

    ratings = [item["rating"] for item in data["movies"]]
    assert ratings == sorted(ratings, reverse=True)

def test_limit_parameter_works_default_and_custom(mocker, client):
    from app.schemas.review import Review
    from app.schemas.movie import Movie

    reviews = [
        Review(
            id=i,
            movieId=f"m{i}",
            authorId=f"a{i}",
            rating=4.0,
            reviewTitle=f"Review {i}",
            reviewBody="Body long enough for leaderboard limit tests.",
            flagged=False,
            votes=i,
            date="2025-11-20",
        )
        for i in range(1, 21)
    ]

    movies = [
        Movie(
            id=f"movie-{i}",
            title=f"Movie {i}",
            year=2025,
            genre="Drama",
            description="Test movie",
            duration=100 + i,
            release="2025-11-20",
            rating=i,
        )
        for i in range(1, 21)
    ]

    mocker.patch(
        "app.services.review_service.list_reviews",
        return_value=reviews,
    )
    mocker.patch(
        "app.services.movie_service.list_movies",
        return_value=movies,
    )

    resp_default = client.get("/leaderboard")
    assert resp_default.status_code == 200
    data_default = resp_default.json()
    assert len(data_default["reviews"]) == 10
    assert len(data_default["movies"]) == 10

    resp_limit_5 = client.get("/leaderboard", params={"limit": 5})
    assert resp_limit_5.status_code == 200
    data_limit_5 = resp_limit_5.json()
    assert len(data_limit_5["reviews"]) == 5
    assert len(data_limit_5["movies"]) == 5

def test_tie_breaking_by_date_recent_first(mocker, client):
    from app.schemas.review import Review
    from app.schemas.movie import Movie

    reviews = [
        Review(
            id=1,
            movieId="m1",
            authorId="a1",
            rating=4.0,
            reviewTitle="Old review",
            reviewBody="Body long enough for tie breaking one.",
            flagged=False,
            votes=10,
            date="2025-11-18",
        ),
        Review(
            id=2,
            movieId="m2",
            authorId="a2",
            rating=4.0,
            reviewTitle="New review",
            reviewBody="Body long enough for tie breaking two.",
            flagged=False,
            votes=10,
            date="2025-11-20",
        ),
        Review(
            id=3,
            movieId="m3",
            authorId="a3",
            rating=4.0,
            reviewTitle="Middle review",
            reviewBody="Body long enough for tie breaking three.",
            flagged=False,
            votes=10,
            date="2025-11-19",
        ),
    ]

    mocker.patch(
        "app.services.review_service.list_reviews",
        return_value=reviews,
    )

    movies = [
        Movie(
            id="movie-1",
            title="Old movie",
            year=2025,
            genre="Drama",
            description="Old movie desc",
            duration=120,
            release="2025-11-18",
            rating=5,
        ),
        Movie(
            id="movie-2",
            title="New movie",
            year=2025,
            genre="Comedy",
            description="New movie desc",
            duration=100,
            release="2025-11-20",
            rating=5,
        ),
        Movie(
            id="movie-3",
            title="Middle movie",
            year=2025,
            genre="Action",
            description="Middle movie desc",
            duration=110,
            release="2025-11-19",
            rating=5,
        ),
    ]

    mocker.patch(
        "app.services.movie_service.list_movies",
        return_value=movies,
    )

    resp = client.get("/leaderboard", params={"limit": 3})
    assert resp.status_code == 200

    data = resp.json()

    ids_in_order = [r["id"] for r in data["reviews"]]
    assert ids_in_order == [2, 3, 1]

    movie_ids_in_order = [m["id"] for m in data["movies"]]
    assert movie_ids_in_order == ["movie-2", "movie-3", "movie-1"]


