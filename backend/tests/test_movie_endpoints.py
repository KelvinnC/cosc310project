import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

def test_list_movies(mocker, client):
    mocker.patch(
        "app.repositories.movie_repo.load_all",
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
    mocker.patch("app.repositories.movie_repo.load_all", return_value=[])
    mock_save = mocker.patch("app.repositories.movie_repo.save_all")
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
    mocker.patch("app.repositories.movie_repo.load_all", return_value=[])
    mocker.patch("app.repositories.movie_repo.save_all")
    response = client.post("/movies", json={})
    assert response.status_code == 422

def test_put_movie_valid_put(mocker, client):
    mocker.patch("app.repositories.movie_repo.load_all",
    return_value=[{
        "id": "1234",
        "title": "Test",
        "genre": "Horror",
        "release": "2022-01-01",
        "description": "Testing Description",
        "duration": 90
    }])
    mocker.patch("app.repositories.movie_repo.save_all")
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
    mocker.patch("app.repositories.movie_repo.load_all",
    return_value=[{
        "id": "1234",
        "title": "Test",
        "genre": "Horror",
        "release": "2022-01-01",
        "description": "Testing Description",
        "duration": 90
    }])
    mocker.patch("app.repositories.movie_repo.save_all")
    response = client.put("/movies/5678", json={
        "title": "InvalidTest",
        "genre": "Horror",
        "release": "2022-01-01",
        "description": "Testing Description",
        "duration": 90
    })
    assert response.status_code == 404

def test_delete_movie_valid_movie(mocker, client):
    mocker.patch("app.repositories.movie_repo.load_all",
    return_value=[{
        "id": "1234",
        "title": "Test",
        "genre": "Horror",
        "release": "2022-01-01",
        "description": "Testing Description",
        "duration": 90
    }])
    mock_save = mocker.patch("app.repositories.movie_repo.save_all")
    response = client.delete("/movies/1234")
    assert(len(mock_save.call_args[0][0]) == 0)
    assert response.status_code == 204

def test_delete_movie_invalid_movie(mocker, client):
    mocker.patch("app.repositories.movie_repo.load_all",
    return_value=[])
    mocker.patch("app.repositories.movie_repo.save_all")
    response = client.delete("/movies/invalidid")
    assert response.status_code == 404

def test_search_all_movies_local_only(mocker, client):
    """When 3+ local results exist, don't query TMDb."""
    from app.schemas.movie import MovieSummary
    mocker.patch(
        "app.services.unified_search_service.search_movies_titles",
        return_value=[
            MovieSummary(id="1", title="Inception Documentary"),
            MovieSummary(id="2", title="Inception Behind the Scenes"),
            MovieSummary(id="3", title="Inception Explained"),
        ]
    )
    mock_tmdb = mocker.patch("app.services.unified_search_service.search_tmdb_movies")
    
    response = client.get("/movies/search/all", params={"title": "inception"})
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["local"]) == 3
    assert len(data["external"]) == 0
    assert data["source"] == "local"
    mock_tmdb.assert_not_called()


def test_search_all_movies_with_tmdb_fallback(mocker, client):
    """When < 3 local results, also query TMDb."""
    from app.schemas.movie import MovieSummary
    from unittest.mock import AsyncMock
    
    mocker.patch(
        "app.services.unified_search_service.search_movies_titles",
        return_value=[MovieSummary(id="1", title="Inception Documentary")]
    )
    mocker.patch(
        "app.services.unified_search_service.search_tmdb_movies",
        new=AsyncMock(return_value=[
            {"tmdb_id": 27205, "title": "Inception", "overview": "A thief...", "release_date": "2010-07-15", "poster_path": "/poster.jpg"}
        ])
    )
    
    response = client.get("/movies/search/all", params={"title": "inception"})
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["local"]) == 1
    assert len(data["external"]) == 1
    assert data["external"][0]["movie_id"] == "tmdb_27205"
    assert data["source"] == "both"


def test_search_all_movies_empty_query(client):
    """Empty query returns 422 validation error."""
    response = client.get("/movies/search/all", params={"title": ""})
    assert response.status_code == 422
