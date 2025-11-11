import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.user import User

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
        active=True,
        warnings=0
    )

