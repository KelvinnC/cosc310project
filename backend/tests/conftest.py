import os
import sys
import pytest

_HERE = os.path.dirname(__file__)
_BACKEND_DIR = os.path.dirname(_HERE)
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

os.environ.setdefault("JWT_SECRET", "testsecret")

@pytest.fixture
def user_data():
    payload = {
        "id": "1234",
        "username": "testmovielover",
        "hashed_password": "$2y$10$b1d2DgDhd1bdRbiwSqfZs.MhtyNCMHaYbQp3.6D3ngYLQ9ySTM/HO",
        "role": "user",
        "created_at": "2025-10-20 16:23:33.447838",
        "active": True,
        "warnings": 0
    }
    return payload

@pytest.fixture
def mock_admin_user():
    import datetime
    return {"user_id": "5678",
                "username": "admin",
                "exp": datetime.datetime.now() + datetime.timedelta(1),
                "role": "admin"}

@pytest.fixture
def mock_unauthorized_user():
    import datetime
    return {"user_id": "1234",
                "username": "user",
                "exp": datetime.datetime.now() + datetime.timedelta(1),
                "role": "user"}