import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routers import user_endpoints
from app.schemas.user import User
from app.middleware.auth_middleware import jwt_auth_dependency

client = TestClient(app)


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


def test_remove_user_warning_success(mocker, mock_admin_user, user_object):
    app.dependency_overrides[jwt_auth_dependency] = lambda: mock_admin_user
    warned_user = user_object.model_copy(update={"warnings": 1})
    mocker.patch("app.services.penalty_service.get_user_by_id_unsafe", return_value=warned_user)
    save = mocker.patch("app.services.penalty_service.save_all")
    response = client.patch(f"/users/{warned_user.id}/unwarn")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["warnings"] == 0
    assert save.called


def test_remove_user_warning_unauthorized(mocker, user_object, mock_unauthorized_user):
    app.dependency_overrides[jwt_auth_dependency] = lambda: mock_unauthorized_user
    mocker.patch("app.services.penalty_service.get_user_by_id_unsafe", return_value=user_object)
    save = mocker.patch("app.services.penalty_service.save_all")
    response = client.patch(f"/users/{user_object.id}/unwarn")
    app.dependency_overrides.clear()
    assert response.status_code == 403
    assert response.json()["detail"] == "Unauthorized action"
    assert not save.called


def test_add_user_ban_success(mocker, mock_admin_user, user_object):
    app.dependency_overrides[jwt_auth_dependency] = lambda: mock_admin_user
    active_user = user_object.model_copy()
    mocker.patch("app.services.penalty_service.get_user_by_id_unsafe",
                 return_value=active_user)
    save = mocker.patch("app.services.penalty_service.save_all")
    response = client.patch(f"/users/{user_object.id}/ban")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["active"] is False
    assert save.called


def test_add_user_ban_unauthorized(mocker, user_object, mock_unauthorized_user):
    app.dependency_overrides[jwt_auth_dependency] = lambda: mock_unauthorized_user
    mocker.patch("app.services.penalty_service.get_user_by_id_unsafe", return_value=user_object)
    save = mocker.patch("app.services.penalty_service.save_all")
    response = client.patch(f"/users/{user_object.id}/ban")
    app.dependency_overrides.clear()
    assert response.status_code == 403
    assert response.json()["detail"] == "Unauthorized action"
    assert not save.called


def test_remove_user_ban_success(mocker, mock_admin_user, user_object):
    app.dependency_overrides[jwt_auth_dependency] = lambda: mock_admin_user
    banned_user = user_object.model_copy(update={"active": False})
    mocker.patch("app.services.penalty_service.get_user_by_id_unsafe", return_value=banned_user)
    save = mocker.patch("app.services.penalty_service.save_all")
    response = client.patch(f"/users/{user_object.id}/unban")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["active"] is True
    assert save.called


def test_remove_user_ban_unauthorized(mocker, user_object, mock_unauthorized_user):
    app.dependency_overrides[jwt_auth_dependency] = lambda: mock_unauthorized_user
    mocker.patch("app.services.penalty_service.get_user_by_id_unsafe", return_value=user_object)
    save = mocker.patch("app.services.penalty_service.save_all")
    response = client.patch(f"/users/{user_object.id}/unban")
    app.dependency_overrides.clear()
    assert response.status_code == 403
    assert response.json()["detail"] == "Unauthorized action"
    assert not save.called
