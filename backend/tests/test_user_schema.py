import pytest
from pydantic import ValidationError
from app.schemas.user import User, UserCreate, UserUpdate

def test_missing_required_fields():
    with pytest.raises(ValidationError):
        User()

def test_valid_user(user_data):
    user = User(**user_data)
    assert user.username == user_data["username"]
    assert user.active is True

def test_valid_user_default_warnings(user_data):
    user = User(**user_data)
    assert user.warnings == user_data["warnings"]

def test_username_too_short(user_data):
    with pytest.raises(ValidationError):
        user_copy = user_data.copy()
        user_copy["username"] = "ab"
        User(**user_copy)

def test_username_too_long(user_data):
    with pytest.raises(ValidationError):
        user_copy = user_data.copy()
        user_copy["username"] = "12345678901234567890abcdefghijklmnopqrstuvwxyz"
        User(**user_copy)

def test_invalid_role(user_data):
    user_copy = user_data.copy()
    user_copy["role"] = "moviehater"
    with pytest.raises(ValidationError):
        User(**user_copy)

def test_user_create_invalid_password():
    new_user = {
        "username": "MyValidUsername",
        "password": "123" #too short
    }
    with pytest.raises(ValidationError):
        UserCreate(**new_user)