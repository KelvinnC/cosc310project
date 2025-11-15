import pytest
from app.schemas.score import ReviewScore
from app.services.score_service import get_reviews_by_author
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

def test_get_score_by_author_id(mocker):
    mocker.patch("app.services.score_service.load_reviews", return_value=[
    {
        "id":  7777,
        "movieId":  "asdfsesfsesfe",
        "date":  "2010-08-31",
        "authorId":  "test_id",
        "reviewTitle":  "Good Movie",
        "reviewBody":  "this is a review body",
        "rating":  4.5,
        "votes":  6,
        "flagged":  False
    }])
    reveiw_score = get_reviews_by_author("test_id")[0]
    assert reveiw_score.reviewTitle == "Good Movie"
    assert reveiw_score.rating == 4.5
    assert reveiw_score.votes == 6
    assert isinstance(reveiw_score, ReviewScore)

def test_get_score(mocker, client):
    mocker.patch("app.services.score_service.load_reviews", return_value=[
        {
            "authorId": "100",
            "reviewTitle": "Best in Venice. Best CBM of all time? Perhaps.",
            "rating": 4.5,
            "votes": 0
        }
    ])
    response = client.get("/score/100")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["reviewTitle"] == "Best in Venice. Best CBM of all time? Perhaps."
    assert data[0]["rating"] == 4.5
    assert data[0]["votes"] == 0