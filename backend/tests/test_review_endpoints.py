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
        "id": "1234",
        "movieId": "1234",
        "authorId": "1234",
        "rating": "5.5",
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "flagged": "False",
        "votes": 5,
        "date": "2022-01-01"
    }])
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

def test_get_review_by_id_valid_id(client):
    response = client.get('/reviews/1234')
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "1234"
    assert data["title"] == "I would not call it a masterpiece as some did"

def test_get_review_by_id_invalid_id(client):
    response = client.get('/reviews/NotAValidID')
    assert response.status_code == 404

def test_post_review_valid_review(mocker, client):
    mocker.patch("app.services.review_service.load_all", return_value=[])
    mock_save = mocker.patch("app.services.review_service.save_all")
    payload = {
        "id": "1234",
        "movieId": "1234",
        "authorId": "1234",
        "rating": "5.5",
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "flagged": "False",
        "votes": 5,
        "date": "2022-01-01"
    }
    response = client.post("/reviews", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test"

def test_post_review_missing_json(mocker, client):
    mocker.patch("app.services.review_service.load_all", return_value=[])
    mocker.patch("app.services.review_service.save_all")
    response = client.post("/reviews", json={})
    assert response.status_code == 422

def test_put_review_valid_put(mocker, client):
    mocker.patch("app.services.review_service.load_all",
    return_value=[{
        "id": "1234",
        "movieId": "1234",
        "authorId": "1234",
        "rating": "5.5",
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "flagged": "False",
        "votes": 5,
        "date": "2022-01-01"
    }])
    mocker.patch("app.services.review_service.save_all")
    response = client.put("/reviews/1234", json={
        "id": "1234",
        "movieId": "1234",
        "authorId": "1234",
        "rating": "5.5",
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "flagged": "False",
        "votes": 5,
        "date": "2022-01-01"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "UpdatedTest"

def test_put_review_invalid_put(mocker, client):
    mocker.patch("app.services.review_service.load_all",
    return_value=[{
        "id": "1234",
        "movieId": "1234",
        "authorId": "1234",
        "rating": "5.5",
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "flagged": "False",
        "votes": 5,
        "date": "2022-01-01"
    }])
    mocker.patch("app.services.review_service.save_all")
    response = client.put("/reviewss/5678", json={
        "id": "1234",
        "movieId": "1234",
        "authorId": "1234",
        "rating": "5.5",
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "flagged": "False",
        "votes": 5,
        "date": "2022-01-01"
    })
    assert response.status_code == 404

def test_delete_review_valid_review(mocker, client):
    mocker.patch("app.services.review_service.load_all",
    return_value=[{
        "id": "1234",
        "movieId": "1234",
        "authorId": "1234",
        "rating": "5.5",
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "flagged": "False",
        "votes": 5,
        "date": "2022-01-01"
    }])
    mock_save = mocker.patch("app.services.review_service.save_all")
    response = client.delete("/review/1234")
    assert(len(mock_save.call_args[0][0]) == 0)
    assert response.status_code == 204

def test_delete_review_invalid_review(mocker, client):
    mocker.patch("app.services.review_service.load_all",
    return_value=[])
    mocker.patch("app.services.review_service.save_all")
    response = client.delete("/reviews/invalidid")
    assert response.status_code == 404