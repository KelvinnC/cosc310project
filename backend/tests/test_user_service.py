import pytest
import datetime
from fastapi import HTTPException
from app.services.user_service import create_user, update_user, get_user_by_id, list_users, delete_user
from app.schemas.user import UserCreate, User, UserUpdate

@pytest.fixture
def user_data():
    payload = {
        "id": "1234",
        "username": "testmovielover",
        "hashed_password": "$2y$10$b1d2DgDhd1bdRbiwSqfZs.MhtyNCMHaYbQp3.6D3ngYLQ9ySTM/HO",
        "role": "user",
        "created_at": datetime.datetime.now(),
        "active": True
    }
    return payload

def test_list_user_empty_list(mocker):
    mocker.patch("app.services.user_service.load_all", return_value=[])
    users = list_users()
    assert users == []

def test_list_user_has_users(mocker, user_data):
    mocker.patch("app.services.user_service.load_all", return_value=[user_data])
    users = list_users()
    assert users[0].id == "1234"
    assert users[0].username == "testmovielover"
    assert users[0].role == "user"
    assert users[0].active == True
    assert len(users) == 1

def test_list_user_deletes_passwords(mocker, user_data):
    mocker.patch("app.services.user_service.load_all", return_value=[user_data])
    users = list_users()
    assert users[0].hashed_password == None

def test_create_user_adds_user(mocker):
    mocker.patch("app.services.user_service.load_all", return_value=[])
    mock_save = mocker.patch("app.services.user_service.save_all")
    mocker.patch("uuid.uuid4", return_value="1234")

    payload = UserCreate(
        username="testmovielover", password="ilovemovies123"
    )

    user = create_user(payload)

    assert user.id == "1234"
    assert user.username == "testmovielover"
    assert user.role == "user"
    assert user.active == True
    assert mock_save.called

def test_create_user_collides_id(mocker, user_data):
    mocker.patch("app.services.user_service.load_all", return_value=[user_data])
    mock_save = mocker.patch("app.services.user_service.save_all")
    mocker.patch("uuid.uuid4", return_value="1234")
    payload = UserCreate(
        username="ialsolovemovies", password="testpass123"
    )
    with pytest.raises(HTTPException) as ex:
        create_user(payload)
    assert ex.value.status_code == 409
    assert ex.value.detail == "ID collision; retry"

def test_create_user_strips_whitespace(mocker):
    mocker.patch("app.services.user_service.load_all", return_value=[])
    mock_save = mocker.patch("app.services.user_service.save_all")
    mocker.patch("uuid.uuid4", return_value="1234")
    payload = UserCreate(
        username="  WhitespaceGuy   ", password="testpass123"
    )
    user = create_user(payload)
    assert user.username == "WhitespaceGuy"
    assert mock_save.called

def test_create_user_hashes_password(mocker, user_data):
    mocker.patch("app.services.user_service.load_all", return_value=[])
    mock_save = mocker.patch("app.services.user_service.save_all")
    mocker.patch("uuid.uuid4", return_value="1234")
    payload = UserCreate(
        username="testmovielover", password="unhashedpassword"
    )
    user = create_user(payload)
    assert user.hashed_password != "unhashedpassword"
    import bcrypt
    assert bcrypt.checkpw("unhashedpassword".encode(), user.hashed_password.encode())

def test_get_user_by_id_valid_id(mocker, user_data):
    mocker.patch("app.services.user_service.load_all", return_value=[user_data])
    user = get_user_by_id("1234")
    assert user.id == "1234"
    assert user.username == "testmovielover"
    assert isinstance(user, User)

def test_get_user_by_id_invalid_id(mocker):
    mocker.patch("app.services.user_service.load_all", return_value=[])
    with pytest.raises(HTTPException) as ex:
        get_user_by_id("1234")
    assert ex.value.status_code == 404
    assert "not found" in ex.value.detail

def test_update_user_valid_update(mocker, user_data):
    mocker.patch("app.services.user_service.load_all", return_value=[user_data])
    mock_save = mocker.patch("app.services.user_service.save_all")
    payload = UserUpdate(
        username="mynewcoolname"
    )
    user = update_user("1234", payload)
    assert user.username == "mynewcoolname"
    assert mock_save.called

def test_update_user_invalid_id(mocker):
    mocker.patch("app.services.user_service.load_all", return_value=[])
    mock_save = mocker.patch("app.services.user_service.save_all")
    payload = UserUpdate(
        username="mynewcoolname"
    )
    with pytest.raises(HTTPException) as ex:
        update_user("1234", payload)
    assert ex.value.status_code == 404
    assert "not found" in ex.value.detail

def test_update_user_password_change(mocker, user_data):
    import bcrypt
    mocker.patch("app.services.user_service.load_all", return_value=[user_data])
    mock_save = mocker.patch("app.services.user_service.save_all")
    new_password = "newpassword123"
    payload = UserUpdate(
        password=new_password
    )
    
    user = update_user("1234", payload)
    assert user.hashed_password != user_data["hashed_password"]
    assert bcrypt.checkpw(new_password.encode(), user.hashed_password.encode())
    assert mock_save.called

def test_delete_user_valid_user(mocker, user_data):
    mocker.patch("app.services.user_service.load_all", return_value=[user_data])
    mock_save = mocker.patch("app.services.user_service.save_all")
    delete_user("1234")
    saved_users = mock_save.call_args[0][0]
    assert all(usr['id'] != "1234" for usr in saved_users)
    assert mock_save.called

def test_delete_user_invalid_user(mocker):
    mocker.patch("app.services.user_service.load_all", return_value=[])
    mock_save = mocker.patch("app.services.user_service.save_all")
    with pytest.raises(HTTPException) as ex:
        delete_user("1234")
    assert ex.value.status_code == 404
    assert "not found" in ex.value.detail