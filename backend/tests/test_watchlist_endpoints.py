import pytest
from fastapi.testclient import TestClient
from app.main import app
from fastapi import HTTPException
from app.routers.user_home import jwt_auth_dependency


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

def test_get_watchlist(mocker, client):
    mock_user_id = 101
    mock_watchlist_data = {
        "id": 50,
        "authorId": mock_user_id,
        "movieIds": ["harry-potter-1", "star-wars-4"]
    }

    app.dependency_overrides[jwt_auth_dependency] = lambda: {"user_id": mock_user_id}

    mocker.patch(
        "app.routers.watchlist_endpoints.get_watchlist_by_author_id", 
        return_value=mock_watchlist_data
    )

    response = client.get("/watchlist")

    app.dependency_overrides = {}

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 50
    assert data["authorId"] == 101
    assert len(data["movieIds"]) == 2

def test_post_watchlist(mocker, client):
    mock_user_id = 101
    new_movie_id = "movie-99"

    mock_updated_watchlist = {
        "id": 50,
        "authorId": mock_user_id,
        "movieIds": ["existing-movie", new_movie_id]
    }

    app.dependency_overrides[jwt_auth_dependency] = lambda: {"user_id": mock_user_id}

    mock_service = mocker.patch(
        "app.routers.watchlist_endpoints.add_movie_to_user_watchlist",
        return_value=mock_updated_watchlist
    )

    response = client.post(
        "/watchlist/add",
        json={"movie_id": new_movie_id}   
    )

    app.dependency_overrides = {}

    assert response.status_code == 201

    data = response.json()
    assert data["id"] == 50
    assert data["authorId"] == mock_user_id
    assert new_movie_id in data["movieIds"]

    mock_service.assert_called_once_with(
        author_id=mock_user_id,
        movie_id=new_movie_id
    )

