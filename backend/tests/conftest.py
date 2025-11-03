import sys
import os

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

os.environ.setdefault("JWT_SECRET", "test-secret-123")
