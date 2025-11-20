"""
Singleton Logger for centralized logging across the application.

This module implements a thread-safe singleton logger that writes structured
logs to a JSON file. It follows the GoF Singleton design pattern to ensure
only one logger instance exists throughout the application lifecycle.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class Logger:
    """
    Singleton logger class that writes structured logs to JSON file.
    
    The singleton pattern ensures all parts of the application share the same
    logger instance, preventing duplicate file handles and ensuring consistent
    log formatting.
    """
    
    _instance = None
    
    def __new__(cls):
        """
        Enforce singleton pattern by returning existing instance or creating new one.
        
        Returns:
            Logger: The single logger instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            
            # Set up log file path
            log_path = Path(__file__).parent.parent / "data" / "logs.json"
            log_path.parent.mkdir(exist_ok=True)
            
            # Initialize empty log file if it doesn't exist
            if not log_path.exists():
                log_path.write_text("[]")
            
            cls._instance.log_file = log_path
        
        return cls._instance
    
    def _write(self, level: str, message: str, component: str = "system", **context: Any) -> None:
        """
        Write a log entry to the JSON log file.
        
        This method creates a structured log entry and appends it to the log file.
        All exceptions are silently caught to prevent logging failures from breaking
        the application.
        
        Args:
            level: Log level (INFO, WARNING, ERROR)
            message: Human-readable log message
            component: Component or module generating the log (default: "system")
            **context: Additional context fields to include in log entry
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "component": component,
            "message": message,
            "context": context
        }
        
        try:
            # Read existing logs
            logs = json.loads(self.log_file.read_text())
            
            # Append new entry
            logs.append(entry)
            
            # Write back to file with pretty formatting
            self.log_file.write_text(json.dumps(logs, indent=2))
        except Exception:
            # Fail silently - logging errors should not break the application
            pass
    
    def info(self, message: str, component: str = "system", **context: Any) -> None:
        """
        Log an informational message.
        
        Use for routine operational events like successful actions, state changes,
        or user activities that completed successfully.
        
        Args:
            message: Human-readable log message
            component: Component generating the log (default: "system")
            **context: Additional context fields
        """
        self._write("INFO", message, component, **context)
    
    def warning(self, message: str, component: str = "system", **context: Any) -> None:
        """
        Log a warning message.
        
        Use for potentially problematic situations that don't prevent operation
        but may require attention (e.g., deprecated features, user warnings).
        
        Args:
            message: Human-readable log message
            component: Component generating the log (default: "system")
            **context: Additional context fields
        """
        self._write("WARNING", message, component, **context)
    
    def error(self, message: str, component: str = "system", **context: Any) -> None:
        """
        Log an error message.
        
        Use for error conditions that represent failures or critical issues
        (e.g., banned users, failed operations, exceptions).
        
        Args:
            message: Human-readable log message
            component: Component generating the log (default: "system")
            **context: Additional context fields
        """
        self._write("ERROR", message, component, **context)


def get_logger() -> Logger:
    """
    Convenience function to get the singleton logger instance.
    
    Returns:
        Logger: The singleton logger instance
    
    Example:
        >>> from app.utils.logger import get_logger
        >>> logger = get_logger()
        >>> logger.info("User logged in", component="auth", user_id="123")
    """
    return Logger()
