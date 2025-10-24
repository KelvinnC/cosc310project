import pytest
from fastapi import HTTPException
from app.services.user_login_service import user_login
from app.schemas.user_login import UserLogin
import os

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT SECRET could not be found")

@pytest.fixture
def user_data():
    user = {
        "id": "77d60efe-0870-4323-b164-3d76474f251f",
        "username": "testuser",
        "hashed_password": "$2b$12$B6mJk/6rXrgrTFnq9YseZu6AIvuEZr1O2lKI6kIa2BJyjyHWz6Kya",
        "role": "user",
        "created_at": "2025-10-23T17:10:27.600472",
        "active": True
  }
    return user

def test_user_login_empty_fields(mocker):
    mocker.patch("app.services.user_login_service.load_all",
                 return_value=[])
    with pytest.raises(HTTPException) as ex:
        user_login(payload=None)
    assert ex.value.status_code == 401

def test_user_login_username_invalid(mocker):
    mocker.patch("app.services.user_login_service.load_all",
                 return_value=[])
    with pytest.raises(HTTPException) as ex:
        user_login(payload="notarealuser")
    assert ex.value.status_code == 401

def test_user_login_password_invalid(mocker, user_data):
    mocker.patch("app.services.user_login_service.load_all",
                 return_value=[user_data])
    with pytest.raises(HTTPException) as ex:
        user_login(payload=UserLogin(username="testuser",
                            password="wrongpassword"))
    assert ex.value.status_code == 401

def test_user_login_credentials_valid(mocker, user_data):
    mocker.patch("app.services.user_login_service.load_all",
                 return_value=[user_data])
    jwt_response = user_login(payload=UserLogin(username="testuser",
                            password="testpass"))
    import jwt
    jwt_decoded = jwt.decode(jwt_response, JWT_SECRET, algorithms=["HS256"])
    assert jwt_decoded["user_id"] == user_data["id"]
    assert jwt_decoded["username"] == user_data["username"]