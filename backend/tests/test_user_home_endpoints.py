import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.user import User
from app.schemas.review import Review
from app.routers.user_home import jwt_auth_dependency

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

def test_get_user_homepage(mocker, client, mock_unauthorized_user, user_data):
    app.dependency_overrides[jwt_auth_dependency] = lambda: mock_unauthorized_user
    mocker.patch("app.services.user_summary_service.get_reviews_by_author", return_value=[Review(**{
        "id": 1,
        "movieId": "1234",
        "authorId": -1,
        "rating": 5.0,
        "reviewTitle": "good movie",
        "reviewBody": "I absolutely loved this movie! The cinematography was stunning and the plot kept me engaged throughout.",
        "flagged": False,
        "votes": 5,
        "date": "2022-01-01"
    })])
    mocker.patch("app.services.user_summary_service.load_user_battles", return_value=["battle1", "battle2"])
    mocker.patch("app.services.user_summary_service.get_user_by_id", return_value=User(**user_data))

    response = client.get("/home")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    user_summary = response.json()
    assert user_summary["battles"] == ["battle1", "battle2"]
    assert user_summary["user"]["username"] == "testmovielover"
    assert user_summary["reviews"][0]["id"] == 1
