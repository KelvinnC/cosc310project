import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

def test_list_reviews(mocker, client):
    mocker.patch("app.services.review_service.load_all",
    return_value=[{
        "id": 1234,
        "movieId": 1234,
        "authorId": 1234,
        "rating": 5.5,
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "flagged": False,
        "votes": 5,
        "date": "2022-01-01"
    }])
    response = client.get("/reviews")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

def test_get_review_by_id_valid_id(mocker, client):
    mocker.patch("app.services.review_service.load_all", return_value=[
        {
            "id": 3,
            "movieId": 123,
            "authorId": 456,
            "rating": 4.0,
            "reviewTitle": "Venice 76 review",
            "reviewBody": "A thoughtful take on the Joker.",
            "flagged": False,
            "votes": 10,
            "date": "2019-10-15"
        }
    ])
    response = client.get('/reviews/3')
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 3
    assert data["reviewTitle"] == "Venice 76 review"

def test_get_review_by_id_invalid_id(mocker, client):
    mocker.patch("app.services.review_service.load_all", return_value=[])
    response = client.get('/reviews/99999')
    assert response.status_code == 404

def test_post_review_valid_review(mocker, client):
    mocker.patch("app.services.review_service.load_all", return_value=[{"id": 5, "movieId": 100, "authorId": 200, "rating": 3.0, "reviewTitle": "old", "reviewBody": "old", "flagged": False, "votes": 0, "date": "2020-01-01"}])
    mock_save = mocker.patch("app.services.review_service.save_all")
    payload = {
        "movieId": 1234,
        "authorId": 1234,
        "rating": 5.5,
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "date": "2022-01-01"
    }
    response = client.post("/reviews", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 6  # Should be max(5) + 1
    assert data["reviewTitle"] == "good movie"
    assert data["movieId"] == 1234
    assert mock_save.called

def test_post_review_missing_json(mocker, client):
    mocker.patch("app.services.review_service.load_all", return_value=[])
    mocker.patch("app.services.review_service.save_all")
    response = client.post("/reviews", json={})
    assert response.status_code == 422

def test_put_review_valid_put(mocker, client):
    mocker.patch("app.services.review_service.load_all",
    return_value=[{
        "id": 1234,
        "movieId": 1234,
        "authorId": 5678,
        "rating": 5.5,
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "flagged": False,
        "votes": 5,
        "date": "2022-01-01"
    }])
    mocker.patch("app.services.review_service.save_all")
    response = client.put("/reviews/1234", json={
        "rating": 4.5,
        "reviewTitle": "updated movie",
        "reviewBody": "updated review body",
        "flagged": False,
        "votes": 10,
        "date": "2022-01-01"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["reviewTitle"] == "updated movie"
    assert data["movieId"] == 1234  # Should preserve original
    assert data["authorId"] == 5678  # Should preserve original
    assert data["votes"] == 10

def test_put_review_invalid_put(mocker, client):
    mocker.patch("app.services.review_service.load_all",
    return_value=[{
        "id": 1234,
        "movieId": 1234,
        "authorId": 1234,
        "rating": 5.5,
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "flagged": False,
        "votes": 5,
        "date": "2022-01-01"
    }])
    mocker.patch("app.services.review_service.save_all")
    response = client.put("/reviewss/5678", json={
        "rating": 5.5,
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "flagged": False,
        "votes": 5,
        "date": "2022-01-01"
    })
    assert response.status_code == 404

def test_delete_review_valid_review(mocker, client):
    mocker.patch("app.services.review_service.load_all",
    return_value=[{
        "id": 1234,
        "movieId": 1234,
        "authorId": 1234,
        "rating": 5.5,
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "flagged": False,
        "votes": 5,
        "date": "2022-01-01"
    }])
    mock_save = mocker.patch("app.services.review_service.save_all")
    response = client.delete("/reviews/1234")
    assert response.status_code == 204
    assert mock_save.called
    assert len(mock_save.call_args[0][0]) == 0

def test_delete_review_invalid_review(mocker, client):
    mocker.patch("app.services.review_service.load_all",
    return_value=[])
    mocker.patch("app.services.review_service.save_all")
    # Path param must be integer; use an integer ID that won't exist
    response = client.delete("/reviews/99999")
    assert response.status_code == 404