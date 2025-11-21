import pytest
import json
from pathlib import Path
from app.services.penalty_service import warn_user, unwarn_user, ban_user, unban_user
from app.services.admin_review_service import hide_review
from app.services.flag_service import flag_review
from app.utils.logger import Logger
from app.schemas.user import User


@pytest.fixture(autouse=True)
def reset_logger():
    Logger._instance = None
    yield
    Logger._instance = None


@pytest.fixture
def mock_user():
    from datetime import datetime
    return User(
        id="test-user-123",
        username="testuser",
        hashed_password="hashed_password",
        role="user",
        created_at=datetime.now(),
        active=True,
        warnings=0
    )


def test_warn_user_logs_action(tmp_path, mocker, mock_user):
    """Verify warn_user logs WARNING level entry"""
    test_log_file = tmp_path / "logs.json"
    test_log_file.write_text("[]")
    logger = Logger()
    logger.log_file = test_log_file
    
    mocker.patch("app.services.penalty_service.logger", logger)
    mocker.patch("app.services.penalty_service.get_user_by_id", 
                 return_value=mock_user)
    mocker.patch("app.services.penalty_service._save_updated_user", 
                 return_value=None)
    
    warn_user("test-user-123")
    
    logs = json.loads(test_log_file.read_text())
    assert len(logs) == 1, "Should have one log entry"
    assert logs[0]["level"] == "WARNING"
    assert logs[0]["component"] == "admin"
    assert "warned" in logs[0]["message"].lower()
    assert logs[0]["context"]["user_id"] == "test-user-123"
    assert logs[0]["context"]["new_warning_count"] == 1


def test_unwarn_user_logs_action(tmp_path, mocker, mock_user):
    """Verify unwarn_user logs INFO level entry"""
    test_log_file = tmp_path / "logs.json"
    test_log_file.write_text("[]")
    logger = Logger()
    logger.log_file = test_log_file
    
    mocker.patch("app.services.penalty_service.logger", logger)
    mock_user.warnings = 2
    mocker.patch("app.services.penalty_service.get_user_by_id", 
                 return_value=mock_user)
    mocker.patch("app.services.penalty_service._save_updated_user", 
                 return_value=None)
    
    unwarn_user("test-user-123")
    
    logs = json.loads(test_log_file.read_text())
    assert len(logs) == 1
    assert logs[0]["level"] == "INFO"
    assert logs[0]["component"] == "admin"
    assert "warning removed" in logs[0]["message"].lower()
    assert logs[0]["context"]["old_warning_count"] == 2
    assert logs[0]["context"]["new_warning_count"] == 1


def test_ban_user_logs_action(tmp_path, mocker, mock_user):
    """Verify ban_user logs ERROR level entry"""
    test_log_file = tmp_path / "logs.json"
    test_log_file.write_text("[]")
    logger = Logger()
    logger.log_file = test_log_file
    
    mocker.patch("app.services.penalty_service.logger", logger)
    mocker.patch("app.services.penalty_service.get_user_by_id", 
                 return_value=mock_user)
    mocker.patch("app.services.penalty_service._save_updated_user", 
                 return_value=None)
    
    ban_user("test-user-123")
    
    logs = json.loads(test_log_file.read_text())
    assert len(logs) == 1
    assert logs[0]["level"] == "ERROR"
    assert logs[0]["component"] == "admin"
    assert "banned" in logs[0]["message"].lower()
    assert logs[0]["context"]["user_id"] == "test-user-123"


def test_unban_user_logs_action(tmp_path, mocker, mock_user):
    """Verify unban_user logs INFO level entry"""
    test_log_file = tmp_path / "logs.json"
    test_log_file.write_text("[]")
    logger = Logger()
    logger.log_file = test_log_file
    
    mocker.patch("app.services.penalty_service.logger", logger)
    mock_user.active = False
    mocker.patch("app.services.penalty_service.get_user_by_id", 
                 return_value=mock_user)
    mocker.patch("app.services.penalty_service._save_updated_user", 
                 return_value=None)
    
    unban_user("test-user-123")
    
    logs = json.loads(test_log_file.read_text())
    assert len(logs) == 1
    assert logs[0]["level"] == "INFO"
    assert logs[0]["component"] == "admin"
    assert "unbanned" in logs[0]["message"].lower()


def test_hide_review_logs_success(tmp_path, mocker):
    """Verify hide_review logs successful hiding"""
    from datetime import date
    test_log_file = tmp_path / "logs.json"
    test_log_file.write_text("[]")
    logger = Logger()
    logger.log_file = test_log_file
    
    mocker.patch("app.services.admin_review_service.logger", logger)
    mock_reviews = [{
        "id": 1, 
        "movieId": "tt1234567",
        "authorId": "author123", 
        "rating": 4.5,
        "reviewTitle": "Great movie",
        "reviewBody": "This was an excellent film with great acting and storyline.",
        "date": date.today().isoformat(),
        "visible": True,
        "flagged": False,
        "votes": 0
    }]
    mocker.patch("app.services.admin_review_service.load_all", 
                 return_value=mock_reviews)
    mocker.patch("app.services.admin_review_service.save_all", 
                 return_value=None)
    
    hide_review(1)
    
    logs = json.loads(test_log_file.read_text())
    assert len(logs) == 1
    assert logs[0]["level"] == "WARNING"
    assert logs[0]["component"] == "admin"
    assert "hidden" in logs[0]["message"].lower()
    assert logs[0]["context"]["review_id"] == 1
    assert logs[0]["context"]["author_id"] == "author123"


def test_hide_review_logs_not_found(tmp_path, mocker):
    """Verify hide_review logs when review not found"""
    test_log_file = tmp_path / "logs.json"
    test_log_file.write_text("[]")
    logger = Logger()
    logger.log_file = test_log_file
    
    mocker.patch("app.services.admin_review_service.logger", logger)
    mocker.patch("app.services.admin_review_service.load_all", 
                 return_value=[])
    
    with pytest.raises(Exception):  # HTTPException
        hide_review(999)
    
    logs = json.loads(test_log_file.read_text())
    assert len(logs) == 1
    assert logs[0]["level"] == "WARNING"
    assert logs[0]["component"] == "admin"
    assert "non-existent" in logs[0]["message"].lower()
    assert logs[0]["context"]["review_id"] == 999


def test_flag_review_logs_action(tmp_path, mocker):
    """Verify flag_review logs flagging action"""
    test_log_file = tmp_path / "logs.json"
    test_log_file.write_text("[]")
    logger = Logger()
    logger.log_file = test_log_file
    
    mocker.patch("app.services.flag_service.logger", logger)
    mock_review = {"id": 1, "text": "Test review", "flagged": False}
    mocker.patch("app.services.flag_service.get_review_by_id", 
                 return_value=mock_review)
    mocker.patch("app.services.flag_service.flag_repo.load_all", 
                 return_value=[])
    mocker.patch("app.services.flag_service.flag_repo.save_all", 
                 return_value=None)
    mocker.patch("app.services.flag_service.mark_review_as_flagged", 
                 return_value=None)
    
    flag_review("user123", 1)
    
    logs = json.loads(test_log_file.read_text())
    assert len(logs) == 1
    assert logs[0]["level"] == "WARNING"
    assert logs[0]["component"] == "moderation"
    assert "flagged" in logs[0]["message"].lower()
    assert logs[0]["context"]["user_id"] == "user123"
    assert logs[0]["context"]["review_id"] == 1
    assert logs[0]["context"]["total_flags"] == 1


def test_duplicate_flag_logs_warning(tmp_path, mocker):
    """Verify duplicate flag attempt logs WARNING"""
    test_log_file = tmp_path / "logs.json"
    test_log_file.write_text("[]")
    logger = Logger()
    logger.log_file = test_log_file
    
    mocker.patch("app.services.flag_service.logger", logger)
    existing_flags = [{"user_id": "user123", "review_id": 1, "timestamp": "2024-01-01T00:00:00"}]
    mock_review = {"id": 1, "text": "Test review", "flagged": True}
    mocker.patch("app.services.flag_service.get_review_by_id", 
                 return_value=mock_review)
    mocker.patch("app.services.flag_service.flag_repo.load_all", 
                 return_value=existing_flags)
    
    with pytest.raises(ValueError, match="already flagged"):
        flag_review("user123", 1)
    
    logs = json.loads(test_log_file.read_text())
    assert len(logs) == 1
    assert logs[0]["level"] == "WARNING"
    assert logs[0]["component"] == "moderation"
    assert "duplicate" in logs[0]["message"].lower()
    assert logs[0]["context"]["user_id"] == "user123"
    assert logs[0]["context"]["review_id"] == 1
