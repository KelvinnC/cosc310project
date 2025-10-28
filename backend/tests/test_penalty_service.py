import pytest
from app.services.penalty_service import warn_user, unwarn_user, ban_user, unban_user
from fastapi import HTTPException
from app.schemas.user import User

@pytest.fixture
def user_object():
    return User(
        id="1234",
        username="testmovielover",
        hashed_password="$2y$10$b1d2DgDhd1bdRbiwSqfZs.MhtyNCMHaYbQp3.6D3ngYLQ9ySTM/HO",
        role="user",
        created_at="2025-10-20 16:23:33.447838",
        active=True,
        warnings=0
    )

def test_penalty_service_valid_warn(mocker, user_object):
    mocker.patch("app.services.penalty_service.get_user_by_id_unsafe",
                 return_value=user_object)
    mocker.patch("app.services.penalty_service.save_all")
    assert user_object.warnings == 0
    user = warn_user(user_object.id)
    assert user.warnings == 1

def test_penalty_service_warn_invalid_user(mocker, user_object):
    mocker.patch("app.services.penalty_service.get_user_by_id_unsafe",
                 return_value=None)
    mocker.patch("app.services.penalty_service.save_all")
    with pytest.raises(HTTPException) as ex:
        warn_user("invalidid")
    assert ex.value.status_code == 404

def test_penalty_service_valid_unwarn(mocker, user_object):
    mocker.patch("app.services.penalty_service.get_user_by_id_unsafe",
                 return_value=user_object)
    mocker.patch("app.services.penalty_service.save_all")
    assert user_object.warnings == 0
    user = unwarn_user(user_object.id)
    assert user.warnings == -1

def test_penalty_service_unwarn_invalid_user(mocker, user_object):
    mocker.patch("app.services.penalty_service.get_user_by_id_unsafe",
                 return_value=None)
    mocker.patch("app.services.penalty_service.save_all")
    with pytest.raises(HTTPException) as ex:
        unwarn_user("invalidid")
    assert ex.value.status_code == 404

def test_penalty_service_valid_ban(mocker, user_object):
    mocker.patch("app.services.penalty_service.get_user_by_id_unsafe",
                 return_value=user_object)
    mocker.patch("app.services.penalty_service.save_all")
    assert user_object.active == True
    user = ban_user(user_object.id)
    assert user.active == False

def test_penalty_service_warn_invalid_ban(mocker, user_object):
    mocker.patch("app.services.penalty_service.get_user_by_id_unsafe",
                 return_value=None)
    mocker.patch("app.services.penalty_service.save_all")
    with pytest.raises(HTTPException) as ex:
        ban_user("invalidid")
    assert ex.value.status_code == 404

def test_penalty_service_valid_unban(mocker, user_object):
    mocker.patch("app.services.penalty_service.get_user_by_id_unsafe",
                 return_value=user_object)
    mocker.patch("app.services.penalty_service.save_all")
    user = unban_user(user_object.id)
    assert user.active == True

def test_penalty_service_warn_invalid_unban(mocker, user_object):
    mocker.patch("app.services.penalty_service.get_user_by_id_unsafe",
                 return_value=None)
    mocker.patch("app.services.penalty_service.save_all")
    with pytest.raises(HTTPException) as ex:
        unban_user("invalidid")
    assert ex.value.status_code == 404