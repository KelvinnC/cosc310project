import pytest
from app.services.admin_user_service import get_user_count, get_warned_users, get_banned_users
from app.schemas.user import User


@pytest.fixture
def warned_users():
    return [
  {
    "id": "1234",
    "username": "admin",
    "hashed_password": "H62THmnBQCLD",
    "role": "admin",
    "created_at": "2025-10-27T21:34:34.307701",
    "active": True,
    "warnings": 0
  },
  {
    "id": "abcd",
    "username": "testuser",
    "hashed_password": "mnjvhMkYV45e",
    "role": "user",
    "created_at": "2025-10-27T21:01:59.674752",
    "active": False,
    "warnings": 5
  }
]


def test_get_user_count_one_user(mocker, user_data):
    mocker.patch("app.services.admin_user_service.load_all", return_value=[user_data])
    total_users = get_user_count()
    assert total_users == 1


def test_get_user_count_no_users(mocker):
    mocker.patch("app.services.admin_user_service.load_all", return_value=[])
    total_users = get_user_count()
    assert total_users == 0


def test_get_warned_users(mocker, warned_users):
    user_objects = [User(**usr) for usr in warned_users]
    mocker.patch("app.services.admin_user_service.list_users", return_value=user_objects)
    total_warned_users = get_warned_users()
    assert len(total_warned_users) == 1
    assert total_warned_users[0].warnings == 5


def test_get_warned_users_no_warned_users(mocker, warned_users):
    user_objects = [User(**usr) for usr in warned_users]
    user_objects[1].warnings = 0
    mocker.patch("app.services.admin_user_service.list_users", return_value=user_objects)
    total_warned_users = get_warned_users()
    assert len(total_warned_users) == 0


def test_get_banned_users(mocker, warned_users):
    user_objects = [User(**usr) for usr in warned_users]
    mocker.patch("app.services.admin_user_service.list_users", return_value=user_objects)
    total_banned_users = get_banned_users()
    assert len(total_banned_users) == 1
    assert total_banned_users[0].active == False


def test_get_banned_users_no_banned_users(mocker, warned_users):
    user_objects = [User(**usr) for usr in warned_users]
    user_objects[1].active = True
    mocker.patch("app.services.admin_user_service.list_users", return_value=user_objects)
    total_banned_users = get_banned_users()
    assert len(total_banned_users) == 0
