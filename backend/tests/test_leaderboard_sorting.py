import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.review import Review


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_endpoint_returns_reviews_in_vote_order(mocker, client):
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

    resp = client.get("/leaderboard")
    assert resp.status_code == 200

    data = resp.json()
    votes = [item["votes"] for item in data]
    assert votes == sorted(votes, reverse=True)


def test_limit_parameter_works_default_and_custom(mocker, client):
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

    mocker.patch(
        "app.services.review_service.list_reviews",
        return_value=reviews,
    )

    resp_default = client.get("/leaderboard")
    assert resp_default.status_code == 200
    data_default = resp_default.json()
    assert len(data_default) == 10

    resp_limit_5 = client.get("/leaderboard", params={"limit": 5})
    assert resp_limit_5.status_code == 200
    data_limit_5 = resp_limit_5.json()
    assert len(data_limit_5) == 5

    votes_default = [r["votes"] for r in data_default]
    votes_limit_5 = [r["votes"] for r in data_limit_5]
    assert votes_default == sorted(votes_default, reverse=True)
    assert votes_limit_5 == sorted(votes_limit_5, reverse=True)


def test_tie_breaking_by_date_recent_first(mocker, client):
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

    resp = client.get("/leaderboard", params={"limit": 3})
    assert resp.status_code == 200

    data = resp.json()
    ids_in_order = [r["id"] for r in data]
    assert ids_in_order == [2, 3, 1]
