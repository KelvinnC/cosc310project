import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

def test_list_movies(mocker, client):
    mocker.patch(
        "app.services.movie_service.load_all",
        return_value=[
            {
                "id": "1234",
                "title": "Test",
                "genre": "Horror",
                "release": "2022-01-01",
                "description": "Testing Description",
                "duration": 90,
            }
        ],
    )
    response = client.get("/movies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert "id" in data[0] and "title" in data[0]

def test_get_movie_by_id_valid_id(client):
    response = client.get("/movies/6bca4027-ad52-414e-810c-b830571cc07d")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == "6bca4027-ad52-414e-810c-b830571cc07d"
    assert data[0]["title"] == "Joker"

def test_get_movie_by_id_invalid_id(client):
    response = client.get("/movies/NotAValidID")
    assert response.status_code == 200
    assert response.json() == []

def test_post_movie_valid_movie(mocker, client):
    mocker.patch("app.services.movie_service.load_all", return_value=[])
    mock_save = mocker.patch("app.services.movie_service.save_all")
    payload = {
        "id": "1234",
        "title": "Test",
        "genre": "Horror",
        "release": "2022-01-01",
        "description": "Testing Description",
        "duration": 90
    }
    response = client.post("/movies", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test"

def test_post_movie_missing_json(mocker, client):
    mocker.patch("app.services.movie_service.load_all", return_value=[])
    mocker.patch("app.services.movie_service.save_all")
    response = client.post("/movies", json={})
    assert response.status_code == 422

def test_put_movie_valid_put(mocker, client):
    mocker.patch("app.services.movie_service.load_all",
    return_value=[{
        "id": "1234",
        "title": "Test",
        "genre": "Horror",
        "release": "2022-01-01",
        "description": "Testing Description",
        "duration": 90
    }])
    mocker.patch("app.services.movie_service.save_all")
    response = client.put("/movies/1234", json={
        "title": "UpdatedTest",
        "genre": "Horror",
        "release": "2022-01-01",
        "description": "Testing Description",
        "duration": 90
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "UpdatedTest"

def test_put_movie_invalid_put(mocker, client):
    mocker.patch("app.services.movie_service.load_all",
    return_value=[{
        "id": "1234",
        "title": "Test",
        "genre": "Horror",
        "release": "2022-01-01",
        "description": "Testing Description",
        "duration": 90
    }])
    mocker.patch("app.services.movie_service.save_all")
    response = client.put("/movies/5678", json={
        "title": "InvalidTest",
        "genre": "Horror",
        "release": "2022-01-01",
        "description": "Testing Description",
        "duration": 90
    })
    assert response.status_code == 404

def test_delete_movie_valid_movie(mocker, client):
    mocker.patch("app.services.movie_service.load_all",
    return_value=[{
        "id": "1234",
        "title": "Test",
        "genre": "Horror",
        "release": "2022-01-01",
        "description": "Testing Description",
        "duration": 90
    }])
    mock_save = mocker.patch("app.services.movie_service.save_all")
    response = client.delete("/movies/1234")
    assert(len(mock_save.call_args[0][0]) == 0)
    assert response.status_code == 204

def test_delete_movie_invalid_movie(mocker, client):
    mocker.patch("app.services.movie_service.load_all",
    return_value=[])
    mocker.patch("app.services.movie_service.save_all")
    response = client.delete("/movies/invalidid")
    assert response.status_code == 404
