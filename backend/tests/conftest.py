from dotenv import load_dotenv
import os
import pytest
import datetime

def pytest_configure():
    load_dotenv()

@pytest.fixture
def user_data():
    payload = {
        "id": "1234",
        "username": "testmovielover",
        "hashed_password": "$2y$10$b1d2DgDhd1bdRbiwSqfZs.MhtyNCMHaYbQp3.6D3ngYLQ9ySTM/HO",
        "role": "user",
        "created_at": datetime.datetime.now(),
        "active": True,
        "warnings": 0
    }
    return payload