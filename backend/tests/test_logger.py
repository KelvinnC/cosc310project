"""
Unit tests for the singleton logger implementation.

Tests verify that the Logger follows the singleton pattern and correctly
writes structured log entries to the JSON log file.
"""

import pytest
import json
from pathlib import Path
from app.utils.logger import Logger, get_logger


def test_singleton_pattern():
    """Verify Logger returns the same instance on multiple calls"""
    # Reset singleton before test
    Logger._instance = None
    
    logger1 = get_logger()
    logger2 = get_logger()
    
    assert logger1 is logger2, "Logger should return the same instance (singleton pattern)"
    
    # Reset after test
    Logger._instance = None


def test_logger_creates_file(tmp_path):
    """Verify logger creates logs.json if it doesn't exist"""
    # Reset singleton before test
    Logger._instance = None
    
    test_log_file = tmp_path / "logs.json"
    test_log_file.parent.mkdir(exist_ok=True)
    
    logger = Logger()
    logger.log_file = test_log_file
    
    # Initialize the file since Logger expects it to exist
    if not test_log_file.exists():
        test_log_file.write_text("[]")
    
    logger.info("Test message", component="test")
    
    assert test_log_file.exists(), "Logger should create log file if it doesn't exist"
    logs = json.loads(test_log_file.read_text())
    assert len(logs) == 1, "Should have one log entry"
    assert logs[0]["message"] == "Test message"
    assert logs[0]["level"] == "INFO"
    assert logs[0]["component"] == "test"
    
    # Reset after test
    Logger._instance = None


def test_logger_writes_multiple_entries(tmp_path):
    """Verify logger appends multiple entries with correct levels"""
    # Reset singleton before test
    Logger._instance = None
    
    test_log_file = tmp_path / "logs.json"
    test_log_file.write_text("[]")
    
    logger = Logger()
    logger.log_file = test_log_file
    
    logger.info("First message", component="test")
    logger.warning("Second message", component="test")
    logger.error("Third message", component="test")
    
    logs = json.loads(test_log_file.read_text())
    assert len(logs) == 3, "Should have three log entries"
    assert logs[0]["level"] == "INFO"
    assert logs[0]["message"] == "First message"
    assert logs[1]["level"] == "WARNING"
    assert logs[1]["message"] == "Second message"
    assert logs[2]["level"] == "ERROR"
    assert logs[2]["message"] == "Third message"
    
    # Reset after test
    Logger._instance = None


def test_logger_includes_context(tmp_path):
    """Verify logger correctly includes context fields"""
    # Reset singleton before test
    Logger._instance = None
    
    test_log_file = tmp_path / "logs.json"
    test_log_file.write_text("[]")
    
    logger = Logger()
    logger.log_file = test_log_file
    
    logger.info("User action", component="auth", user_id="123", action="login")
    
    logs = json.loads(test_log_file.read_text())
    assert len(logs) == 1
    assert logs[0]["context"]["user_id"] == "123"
    assert logs[0]["context"]["action"] == "login"
    
    # Reset after test
    Logger._instance = None


def test_logger_includes_timestamp(tmp_path):
    """Verify logger includes ISO format timestamp"""
    # Reset singleton before test
    Logger._instance = None
    
    test_log_file = tmp_path / "logs.json"
    test_log_file.write_text("[]")
    
    logger = Logger()
    logger.log_file = test_log_file
    
    logger.info("Test", component="test")
    
    logs = json.loads(test_log_file.read_text())
    assert "timestamp" in logs[0]
    assert logs[0]["timestamp"].endswith("Z"), "Timestamp should be in UTC with Z suffix"
    
    # Reset after test
    Logger._instance = None
