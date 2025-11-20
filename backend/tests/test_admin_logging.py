"""
Integration tests for admin service logging.

Tests verify that admin and moderation operations correctly log their actions
with appropriate log levels and context information.
"""

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
    """Reset singleton before and after each test"""
    Logger._instance = None
    yield
    Logger._instance = None


@pytest.fixture
def mock_user():
    """Mock user for testing"""
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


def test_warn_user_logs_action(tmp_path, monkeypatch, mock_user):
    """Verify warn_user logs WARNING level entry"""
    test_log_file = tmp_path / "logs.json"
    test_log_file.write_text("[]")
    logger = Logger()
    logger.log_file = test_log_file
    
    monkeypatch.setattr("app.services.penalty_service.get_user_by_id_unsafe", 
                       lambda uid: mock_user)
    monkeypatch.setattr("app.services.penalty_service._save_updated_user", 
                       lambda u, uid: None)
    
    warn_user("test-user-123")
    
    logs = json.loads(test_log_file.read_text())
    assert len(logs) == 1, "Should have one log entry"
    assert logs[0]["level"] == "WARNING"
    assert logs[0]["component"] == "admin"
    assert "warned" in logs[0]["message"].lower()
    assert logs[0]["context"]["user_id"] == "test-user-123"
    assert logs[0]["context"]["new_warning_count"] == 1


def test_unwarn_user_logs_action(tmp_path, monkeypatch, mock_user):
    """Verify unwarn_user logs INFO level entry"""
    test_log_file = tmp_path / "logs.json"
    test_log_file.write_text("[]")
    logger = Logger()
    logger.log_file = test_log_file
    
    mock_user.warnings = 2
    monkeypatch.setattr("app.services.penalty_service.get_user_by_id_unsafe", 
                       lambda uid: mock_user)
    monkeypatch.setattr("app.services.penalty_service._save_updated_user", 
                       lambda u, uid: None)
    
    unwarn_user("test-user-123")
    
    logs = json.loads(test_log_file.read_text())
    assert len(logs) == 1
    assert logs[0]["level"] == "INFO"
    assert logs[0]["component"] == "admin"
    assert "warning removed" in logs[0]["message"].lower()
    assert logs[0]["context"]["old_warning_count"] == 2
    assert logs[0]["context"]["new_warning_count"] == 1


def test_ban_user_logs_action(tmp_path, monkeypatch, mock_user):
    """Verify ban_user logs ERROR level entry"""
    test_log_file = tmp_path / "logs.json"
    test_log_file.write_text("[]")
    logger = Logger()
    logger.log_file = test_log_file
    
    monkeypatch.setattr("app.services.penalty_service.get_user_by_id_unsafe", 
                       lambda uid: mock_user)
    monkeypatch.setattr("app.services.penalty_service._save_updated_user", 
                       lambda u, uid: None)
    
    ban_user("test-user-123")
    
    logs = json.loads(test_log_file.read_text())
    assert len(logs) == 1
    assert logs[0]["level"] == "ERROR"
    assert logs[0]["component"] == "admin"
    assert "banned" in logs[0]["message"].lower()
    assert logs[0]["context"]["user_id"] == "test-user-123"


def test_unban_user_logs_action(tmp_path, monkeypatch, mock_user):
    """Verify unban_user logs INFO level entry"""
    test_log_file = tmp_path / "logs.json"
    test_log_file.write_text("[]")
    logger = Logger()
    logger.log_file = test_log_file
    
    mock_user.active = False
    monkeypatch.setattr("app.services.penalty_service.get_user_by_id_unsafe", 
                       lambda uid: mock_user)
    monkeypatch.setattr("app.services.penalty_service._save_updated_user", 
                       lambda u, uid: None)
    
    unban_user("test-user-123")
    
    logs = json.loads(test_log_file.read_text())
    assert len(logs) == 1
    assert logs[0]["level"] == "INFO"
    assert logs[0]["component"] == "admin"
    assert "unbanned" in logs[0]["message"].lower()


def test_hide_review_logs_success(tmp_path, monkeypatch):
    """Verify hide_review logs successful hiding"""
    from datetime import date
    test_log_file = tmp_path / "logs.json"
    test_log_file.write_text("[]")
    logger = Logger()
    logger.log_file = test_log_file
    
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
    monkeypatch.setattr("app.services.admin_review_service.load_all", 
                       lambda load_invisible=False: mock_reviews)
    monkeypatch.setattr("app.services.admin_review_service.save_all", 
                       lambda reviews: None)
    
    hide_review(1)
    
    logs = json.loads(test_log_file.read_text())
    assert len(logs) == 1
    assert logs[0]["level"] == "WARNING"
    assert logs[0]["component"] == "admin"
    assert "hidden" in logs[0]["message"].lower()
    assert logs[0]["context"]["review_id"] == 1
    assert logs[0]["context"]["author_id"] == "author123"


def test_hide_review_logs_not_found(tmp_path, monkeypatch):
    """Verify hide_review logs when review not found"""
    test_log_file = tmp_path / "logs.json"
    test_log_file.write_text("[]")
    logger = Logger()
    logger.log_file = test_log_file
    
    monkeypatch.setattr("app.services.admin_review_service.load_all", 
                       lambda load_invisible=False: [])
    
    with pytest.raises(Exception):  # HTTPException
        hide_review(999)
    
    logs = json.loads(test_log_file.read_text())
    assert len(logs) == 1
    assert logs[0]["level"] == "WARNING"
    assert logs[0]["component"] == "admin"
    assert "non-existent" in logs[0]["message"].lower()
    assert logs[0]["context"]["review_id"] == 999


def test_flag_review_logs_action(tmp_path, monkeypatch):
    """Verify flag_review logs flagging action"""
    test_log_file = tmp_path / "logs.json"
    test_log_file.write_text("[]")
    logger = Logger()
    logger.log_file = test_log_file
    
    mock_review = {"id": 1, "text": "Test review", "flagged": False}
    monkeypatch.setattr("app.services.flag_service.get_review_by_id", 
                       lambda rid: mock_review)
    monkeypatch.setattr("app.services.flag_service.flag_repo.load_all", 
                       lambda: [])
    monkeypatch.setattr("app.services.flag_service.flag_repo.save_all", 
                       lambda flags: None)
    monkeypatch.setattr("app.services.flag_service.mark_review_as_flagged", 
                       lambda review: None)
    
    flag_review("user123", 1)
    
    logs = json.loads(test_log_file.read_text())
    assert len(logs) == 1
    assert logs[0]["level"] == "WARNING"
    assert logs[0]["component"] == "moderation"
    assert "flagged" in logs[0]["message"].lower()
    assert logs[0]["context"]["user_id"] == "user123"
    assert logs[0]["context"]["review_id"] == 1
    assert logs[0]["context"]["total_flags"] == 1


def test_duplicate_flag_logs_warning(tmp_path, monkeypatch):
    """Verify duplicate flag attempt logs WARNING"""
    test_log_file = tmp_path / "logs.json"
    test_log_file.write_text("[]")
    logger = Logger()
    logger.log_file = test_log_file
    
    existing_flags = [{"user_id": "user123", "review_id": 1, "timestamp": "2024-01-01T00:00:00"}]
    mock_review = {"id": 1, "text": "Test review", "flagged": True}
    monkeypatch.setattr("app.services.flag_service.get_review_by_id", 
                       lambda rid: mock_review)
    monkeypatch.setattr("app.services.flag_service.flag_repo.load_all", 
                       lambda: existing_flags)
    
    with pytest.raises(ValueError, match="already flagged"):
        flag_review("user123", 1)
    
    logs = json.loads(test_log_file.read_text())
    assert len(logs) == 1
    assert logs[0]["level"] == "WARNING"
    assert logs[0]["component"] == "moderation"
    assert "duplicate" in logs[0]["message"].lower()
    assert logs[0]["context"]["user_id"] == "user123"
    assert logs[0]["context"]["review_id"] == 1
