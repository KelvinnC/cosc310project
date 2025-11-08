import pytest
from app.services.admin_service import load_all, get_user_count

def test_get_user_count_one_user(mocker, user_data):
    mocker.patch("app.services.admin_service.load_all", return_value=[user_data])
    total_users = get_user_count()
    assert total_users == 1

def test_get_user_count_no_users(mocker):
    mocker.patch("app.services.admin_service.load_all", return_value=[])
    total_users = get_user_count()
    assert total_users == 0