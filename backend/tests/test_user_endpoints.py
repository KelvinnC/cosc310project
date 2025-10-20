import pytest
from fastapi.testclient import TestClient
from app.main import app
import datetime

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def user_data():
    payload = {
        "id": "1234",
        "username": "testmovielover",
        "hashed_password": "$2y$10$b1d2DgDhd1bdRbiwSqfZs.MhtyNCMHaYbQp3.6D3ngYLQ9ySTM/HO",
        "role": "user",
        "created_at": "2025-10-20 16:23:33.447838",
        "active": True
    }
    return payload

def test_list_users(mocker, client, user_data):
    mocker.patch("app.services.user_service.load_all",
    return_value=[user_data])
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

def test_get_user_by_id_valid_id(mocker, client, user_data):
    mocker.patch("app.services.user_service.load_all",
    return_value=[user_data])
    response = client.get('/users/1234')
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "1234"
    assert data["username"] == "testmovielover"

def test_get_user_by_id_invalid_id(client):
    response = client.get('/users/NotAValidID')
    assert response.status_code == 404

def test_post_user_valid_user(mocker, client):
    mocker.patch("app.services.user_service.load_all", return_value=[])
    mock_save = mocker.patch("app.services.user_service.save_all")
    response = client.post("/users", json={"username": "testmovielover", "password": "mymoviepassword"})
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testmovielover"

def test_post_user_missing_json(mocker, client):
    mocker.patch("app.services.user_service.load_all", return_value=[])
    mocker.patch("app.services.user_service.save_all")
    response = client.post("/users", json={})
    assert response.status_code == 422

def test_put_user_valid_put(mocker, client, user_data):
    mocker.patch("app.services.user_service.load_all",
    return_value=[user_data])
    mocker.patch("app.services.user_service.save_all")
    response = client.put("/users/1234", json={
        "username": "newusername",
        "password": "mynewpassword123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newusername"

def test_put_user_invalid_put(mocker, client, user_data):
    mocker.patch("app.services.user_service.load_all",
    return_value=[user_data])
    mocker.patch("app.services.user_service.save_all")
    response = client.put("/users/5678", json={
        "username": "thiswontupdate"
        })
    assert response.status_code == 404

def test_delete_user_valid_user(mocker, client, user_data):
    mocker.patch("app.services.user_service.load_all",
    return_value=[user_data])
    mock_save = mocker.patch("app.services.user_service.save_all")
    response = client.delete("/users/1234")
    assert(len(mock_save.call_args[0][0]) == 0)
    assert response.status_code == 204

def test_delete_user_invalid_user(mocker, client):
    mocker.patch("app.services.user_service.load_all",
    return_value=[])
    mocker.patch("app.services.user_service.save_all")
    response = client.delete("/users/invalidid")
    assert response.status_code == 404