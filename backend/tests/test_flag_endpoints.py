import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.middleware.auth_middleware import jwt_auth_dependency
from fastapi import HTTPException


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_user():
    return {"user_id": "user-123", "username": "testuser", "role": "user"}


def test_flag_review_requires_authentication(mocker, client):
    """Test that flag endpoint requires authentication"""
    response = client.post("/reviews/1/flag")
    
    assert response.status_code == 401


def test_flag_review_success(mocker, client, mock_user):
    """Test successfully flagging a review"""
    app.dependency_overrides[jwt_auth_dependency] = lambda: mock_user
    
    mock_flag_service = mocker.patch("app.routers.reviews.flag_service.flag_review")
    mock_flag_service.return_value = {
        "user_id": "user-123",
        "review_id": 1,
        "timestamp": "2023-01-15T10:00:00"
    }
    
    response = client.post("/reviews/1/flag")
    app.dependency_overrides.clear()
    
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Review flagged successfully"
    assert data["review_id"] == 1
    assert "flagged_at" in data


def test_flag_review_duplicate_returns_409(mocker, client, mock_user):
    """Test that duplicate flag returns 409 Conflict"""
    app.dependency_overrides[jwt_auth_dependency] = lambda: mock_user
    
    mock_flag_service = mocker.patch("app.routers.reviews.flag_service.flag_review")
    mock_flag_service.side_effect = ValueError("User has already flagged this review")
    
    response = client.post("/reviews/1/flag")
    app.dependency_overrides.clear()
    
    assert response.status_code == 409
    assert "already flagged" in response.json()["detail"].lower()


def test_flag_review_invalid_review_returns_404(mocker, client, mock_user):
    """Test flagging non-existent review returns 404"""
    from fastapi import HTTPException
    
    app.dependency_overrides[jwt_auth_dependency] = lambda: mock_user
    
    mock_flag_service = mocker.patch("app.routers.reviews.flag_service.flag_review")
    mock_flag_service.side_effect = HTTPException(status_code=404, detail="Review not found")
    
    response = client.post("/reviews/999/flag")
    app.dependency_overrides.clear()
    
    assert response.status_code == 404


def test_flag_review_other_value_error_returns_400(mocker, client, mock_user):
    """Test that other ValueError returns 400"""
    app.dependency_overrides[jwt_auth_dependency] = lambda: mock_user
    
    mock_flag_service = mocker.patch("app.routers.reviews.flag_service.flag_review")
    mock_flag_service.side_effect = ValueError("Some other validation error")
    
    response = client.post("/reviews/1/flag")
    app.dependency_overrides.clear()
    
    assert response.status_code == 400
    assert "validation error" in response.json()["detail"].lower()


def test_flag_review_generic_exception_returns_500(mocker, client, mock_user):
    """Test that generic exception returns 500"""
    app.dependency_overrides[jwt_auth_dependency] = lambda: mock_user
    
    mock_flag_service = mocker.patch("app.routers.reviews.flag_service.flag_review")
    mock_flag_service.side_effect = Exception("Unexpected error")
    
    response = client.post("/reviews/1/flag")
    app.dependency_overrides.clear()
    
    assert response.status_code == 500


def test_flag_review_extracts_user_id_from_jwt(mocker, client, mock_user):
    """Test that user_id is correctly extracted from JWT token"""
    app.dependency_overrides[jwt_auth_dependency] = lambda: mock_user
    
    mock_flag_service = mocker.patch("app.routers.reviews.flag_service.flag_review")
    mock_flag_service.return_value = {
        "user_id": "user-123",
        "review_id": 1,
        "timestamp": "2023-01-15T10:00:00"
    }
    
    response = client.post("/reviews/1/flag")
    app.dependency_overrides.clear()
    
    # Verify flag_service was called with correct user_id from JWT
    mock_flag_service.assert_called_once_with("user-123", 1)
    assert response.status_code == 201


def test_flag_review_invalid_path_param_returns_422(client):
    """Non-integer review_id should trigger FastAPI validation (422)"""
    from app.middleware.auth_middleware import jwt_auth_dependency
    from app.main import app
    app.dependency_overrides[jwt_auth_dependency] = lambda: {"user_id": "u-x", "username": "x", "role": "user"}
    try:
        resp = client.post("/reviews/abc/flag")
        assert resp.status_code == 422
    finally:
        app.dependency_overrides.clear()

def test_unflag_review_success(mocker, client, mock_admin_user):
    """Test successfully unflagging a review"""
    app.dependency_overrides[jwt_auth_dependency] = lambda: mock_admin_user
    
    mock_unflag_service = mocker.patch("app.routers.reviews.flag_service.unflag_review")
    
    response = client.post("/reviews/1/unflag")
    app.dependency_overrides.clear()
    
    assert response.status_code == 204
    
def test_unflag_review_not_found(mocker, client, mock_admin_user):
    """Test flagging a review that is not found"""
    app.dependency_overrides[jwt_auth_dependency] = lambda: mock_admin_user
    
    mock_unflag_service = mocker.patch("app.routers.reviews.flag_service.unflag_review", side_effect=HTTPException(status_code=404, detail="Review Not Found"))
    
    response = client.post("/reviews/123/unflag")
    app.dependency_overrides.clear()
    
    assert response.status_code == 404