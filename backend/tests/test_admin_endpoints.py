import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.user import User
from app.routers.admin_endpoints import jwt_auth_dependency

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def penalized_user():
    return User(
        id="1234",
        username="testmovielover",
        hashed_password="$2y$10$b1d2DgDhd1bdRbiwSqfZs.MhtyNCMHaYbQp3.6D3ngYLQ9ySTM/HO",
        role="user",
        created_at="2025-10-20 16:23:33.447838",
        active=False,
        warnings=1
    )

def test_admin_summary_authorized_user(mocker, client, mock_admin_user, penalized_user):
    app.dependency_overrides[jwt_auth_dependency] = lambda: mock_admin_user
    mocker.patch("app.routers.admin_endpoints.get_user_count", return_value=1)
    mocker.patch("app.routers.admin_endpoints.get_banned_users", return_value=[penalized_user])
    mocker.patch("app.routers.admin_endpoints.get_warned_users", return_value=[penalized_user])
    response = client.get("/admin")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    res = response.json()
    assert res["total_users"] == 1
    assert all(user["active"] == False for user in res["banned_users"])
    assert all(user["warnings"] > 0 for user in res["warned_users"])
    assert all(review["flagged"] for review in res["flagged_reviews"])

def test_admin_summary_unauthorized_user(mocker, client, mock_unauthorized_user, penalized_user):
    app.dependency_overrides[jwt_auth_dependency] = lambda: mock_unauthorized_user
    mocker.patch("app.routers.admin_endpoints.get_user_count", return_value=1)
    mocker.patch("app.routers.admin_endpoints.get_banned_users", return_value=[penalized_user])
    mocker.patch("app.routers.admin_endpoints.get_warned_users", return_value=[penalized_user])
    response = client.get("/admin")
    app.dependency_overrides.clear()
    assert response.status_code == 403