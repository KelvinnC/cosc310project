import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class Logger:
    """Thread-safe singleton logger that writes structured logs to JSON"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Return singleton instance"""
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
        """Write log entry to JSON file"""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": level,
            "component": component,
            "message": message,
            "context": context
        }
        
        with self._lock:
            try:
                logs = json.loads(self.log_file.read_text())
                logs.append(entry)
                self.log_file.write_text(json.dumps(logs, indent=2))
            except Exception:
                pass
    
    def info(self, message: str, component: str = "system", **context: Any) -> None:
        """Log INFO level message"""
        self._write("INFO", message, component, **context)
    
    def warning(self, message: str, component: str = "system", **context: Any) -> None:
        """Log WARNING level message"""
        self._write("WARNING", message, component, **context)
    
    def error(self, message: str, component: str = "system", **context: Any) -> None:
        """Log ERROR level message"""
        self._write("ERROR", message, component, **context)


def get_logger() -> Logger:
    """Get singleton logger instance"""
    return Logger()
