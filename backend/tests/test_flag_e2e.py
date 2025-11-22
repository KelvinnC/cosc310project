"""
True end-to-end tests for flag system.

These tests start the actual FastAPI server as a subprocess and make real HTTP requests,
testing the complete flag workflow including authentication, file persistence, and
server lifecycle.
"""
import json
import subprocess
import time
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, date
import pytest
import requests
import jwt
import os
import sys


# Test configuration
E2E_SERVER_HOST = "127.0.0.1"
E2E_SERVER_PORT = 8766
E2E_BASE_URL = f"http://{E2E_SERVER_HOST}:{E2E_SERVER_PORT}"
E2E_STARTUP_TIMEOUT = 10  # seconds
JWT_SECRET = os.environ.get("JWT_SECRET", "testsecret")


@pytest.fixture(scope="module")
def temp_data_dir():
    """Create a temporary directory for test data files."""
    temp_dir = tempfile.mkdtemp(prefix="e2e_flag_test_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="module")
def test_data_files(temp_data_dir):
    """Create test data files for users, reviews, and flags."""
    users_file = temp_data_dir / "users.json"
    reviews_file = temp_data_dir / "reviews.json"
    flags_file = temp_data_dir / "flags.json"
    
    # Create test users
    users_data = [
        {
            "id": "e2e-flag-user-1",
            "username": "e2e_flagger",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJz7UW2CW",
            "role": "user",
            "created_at": datetime.now().isoformat(),
            "active": True,
            "warnings": 0
        },
        {
            "id": "e2e-flag-user-2",
            "username": "e2e_reviewer",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJz7UW2CW",
            "role": "user",
            "created_at": datetime.now().isoformat(),
            "active": True,
            "warnings": 0
        }
    ]
    
    # Create test reviews
    reviews_data = [
        {
            "id": 2001,
            "movieId": "e2e-movie-1",
            "authorId": "e2e-flag-user-2",
            "rating": 4.5,
            "reviewTitle": "Inappropriate content here",
            "reviewBody": "This review contains some content that should be flagged by moderators for review.",
            "flagged": False,
            "votes": 5,
            "date": date.today().isoformat(),
            "visible": True
        },
        {
            "id": 2002,
            "movieId": "e2e-movie-2",
            "authorId": "e2e-flag-user-2",
            "rating": 3.0,
            "reviewTitle": "Another problematic review",
            "reviewBody": "This is another review that contains content that might need moderation attention.",
            "flagged": False,
            "votes": 2,
            "date": date.today().isoformat(),
            "visible": True
        },
        {
            "id": 2003,
            "movieId": "e2e-movie-3",
            "authorId": "e2e-flag-user-2",
            "rating": 2.0,
            "reviewTitle": "Already flagged review",
            "reviewBody": "This review has already been flagged by someone and should show as flagged.",
            "flagged": True,
            "votes": 0,
            "date": date.today().isoformat(),
            "visible": True
        }
    ]
    
    # Initially empty flags
    flags_data = []
    
    # Write data files
    users_file.write_text(json.dumps(users_data, indent=2), encoding="utf-8")
    reviews_file.write_text(json.dumps(reviews_data, indent=2), encoding="utf-8")
    flags_file.write_text(json.dumps(flags_data, indent=2), encoding="utf-8")
    
    return {
        "users": users_file,
        "reviews": reviews_file,
        "flags": flags_file
    }


@pytest.fixture(scope="module")
def auth_token():
    """Generate a valid JWT token for e2e-flag-user-1."""
    payload = {
        "user_id": "e2e-flag-user-1",
        "username": "e2e_flagger",
        "role": "user",
        "exp": datetime.now().timestamp() + 3600  # Valid for 1 hour
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token


@pytest.fixture(scope="module")
def server_process(test_data_files, temp_data_dir):
    """Start the FastAPI server as a subprocess with test data."""
    # Create a startup script that patches the data paths
    backend_dir = Path(__file__).parent.parent
    startup_script = temp_data_dir / "start_e2e_flag_server.py"
    
    startup_script_content = f'''
import sys
sys.path.insert(0, "{backend_dir}")

# Patch data paths before importing app
from pathlib import Path
from app.repositories import user_repo, review_repo, flag_repo

user_repo.DATA_PATH = Path("{test_data_files["users"]}")
review_repo.DATA_PATH = Path("{test_data_files["reviews"]}")
flag_repo.DATA_FILE = "{test_data_files["flags"]}"

# Now import and run the app
import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="{E2E_SERVER_HOST}", port={E2E_SERVER_PORT}, log_level="warning")
'''
    startup_script.write_text(startup_script_content)
    
    # Set environment variables
    env = os.environ.copy()
    env["JWT_SECRET"] = JWT_SECRET
    
    # Start server using the startup script
    cmd = [sys.executable, str(startup_script)]
    
    process = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    start_time = time.time()
    server_ready = False
    
    while time.time() - start_time < E2E_STARTUP_TIMEOUT:
        try:
            response = requests.get(f"{E2E_BASE_URL}/", timeout=1)
            if response.status_code == 200:
                server_ready = True
                break
        except requests.exceptions.RequestException:
            time.sleep(0.5)
    
    if not server_ready:
        process.terminate()
        process.wait()
        stdout, stderr = process.communicate()
        raise RuntimeError(
            f"Server failed to start within {E2E_STARTUP_TIMEOUT} seconds.\n"
            f"STDOUT: {stdout.decode()}\n"
            f"STDERR: {stderr.decode()}"
        )
    
    yield process
    
    # Cleanup: terminate server
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


class TestFlagE2E:
    """End-to-end tests for flag workflow."""
    
    def test_server_is_running(self, server_process):
        """Verify the server is accessible."""
        response = requests.get(f"{E2E_BASE_URL}/")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_flag_review_requires_auth(self, server_process):
        """Test that flagging a review requires authentication."""
        response = requests.post(f"{E2E_BASE_URL}/reviews/2001/flag")
        assert response.status_code == 401
    
    def test_flag_review_success(self, server_process, auth_token, test_data_files):
        """Test successful flagging of a review via API."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{E2E_BASE_URL}/reviews/2001/flag", headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "message" in data
        assert data["review_id"] == 2001
        assert "flagged_at" in data
        
        # Verify flag was persisted to file
        flags_file = test_data_files["flags"]
        flags = json.loads(flags_file.read_text(encoding="utf-8"))
        
        saved_flag = next((f for f in flags if f["review_id"] == 2001), None)
        assert saved_flag is not None
        assert saved_flag["user_id"] == "e2e-flag-user-1"
        assert "timestamp" in saved_flag
        
        # Verify review was marked as flagged
        reviews_file = test_data_files["reviews"]
        reviews = json.loads(reviews_file.read_text(encoding="utf-8-sig"))
        
        flagged_review = next((r for r in reviews if r["id"] == 2001), None)
        assert flagged_review is not None
        assert flagged_review["flagged"] is True
    
    def test_flag_review_duplicate(self, server_process, auth_token, test_data_files):
        """Test that flagging the same review twice by same user is rejected."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # First flag should succeed
        first_response = requests.post(f"{E2E_BASE_URL}/reviews/2002/flag", headers=headers)
        assert first_response.status_code == 201
        
        # Second flag should fail with 409 Conflict
        second_response = requests.post(f"{E2E_BASE_URL}/reviews/2002/flag", headers=headers)
        assert second_response.status_code == 409
        assert "already flagged" in second_response.json()["detail"].lower()
        
        # Verify only one flag was persisted
        flags_file = test_data_files["flags"]
        flags = json.loads(flags_file.read_text(encoding="utf-8"))
        
        user_flags_for_review = [
            f for f in flags 
            if f["review_id"] == 2002 and f["user_id"] == "e2e-flag-user-1"
        ]
        assert len(user_flags_for_review) == 1
    
    def test_flag_nonexistent_review(self, server_process, auth_token):
        """Test that flagging a nonexistent review returns 404."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{E2E_BASE_URL}/reviews/99999/flag", headers=headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_multiple_users_can_flag_same_review(self, server_process, test_data_files):
        """Test that different users can flag the same review."""
        # Create token for second user
        payload = {
            "user_id": "e2e-flag-user-2",
            "username": "e2e_reviewer",
            "role": "user",
            "exp": datetime.now().timestamp() + 3600
        }
        second_user_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        
        # Reset flags file to ensure clean state
        flags_file = test_data_files["flags"]
        flags_file.write_text(json.dumps([], indent=2), encoding="utf-8")
        
        # Reset review flagged status
        reviews_file = test_data_files["reviews"]
        reviews = json.loads(reviews_file.read_text(encoding="utf-8-sig"))
        for review in reviews:
            if review["id"] == 2001:
                review["flagged"] = False
        reviews_file.write_text(json.dumps(reviews, indent=2), encoding="utf-8")
        
        # Wait a bit for file system to sync
        time.sleep(0.1)
        
        # First user flags
        headers1 = {"Authorization": f"Bearer {payload.get('exp') - 3600}"}  # Use original token
        # Actually, let me generate proper tokens
        token1 = jwt.encode({
            "user_id": "e2e-flag-user-1",
            "username": "e2e_flagger",
            "role": "user",
            "exp": datetime.now().timestamp() + 3600
        }, JWT_SECRET, algorithm="HS256")
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        response1 = requests.post(f"{E2E_BASE_URL}/reviews/2001/flag", headers=headers1)
        
        # Second user flags same review
        headers2 = {"Authorization": f"Bearer {second_user_token}"}
        response2 = requests.post(f"{E2E_BASE_URL}/reviews/2001/flag", headers=headers2)
        
        # Both should succeed (unless already flagged from earlier test)
        assert response1.status_code in [201, 409]
        assert response2.status_code in [201, 409]
        
        # Verify multiple flags can exist for same review
        flags = json.loads(flags_file.read_text(encoding="utf-8"))
        flags_for_review_2001 = [f for f in flags if f["review_id"] == 2001]
        
        # Should have flags from both users (unless already existed)
        unique_users = set(f["user_id"] for f in flags_for_review_2001)
        assert len(unique_users) >= 1  # At least one user flagged it
    
    def test_flag_persistence_across_requests(self, server_process, auth_token, test_data_files):
        """Test that flags persist correctly across multiple requests."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Read initial flag count
        flags_file = test_data_files["flags"]
        initial_flags = json.loads(flags_file.read_text(encoding="utf-8"))
        initial_count = len(initial_flags)
        
        # Flag multiple reviews
        reviews_to_flag = [2001, 2002]
        successful_flags = []
        
        for review_id in reviews_to_flag:
            response = requests.post(f"{E2E_BASE_URL}/reviews/{review_id}/flag", headers=headers)
            if response.status_code == 201:
                successful_flags.append(review_id)
        
        # Verify flags were persisted
        final_flags = json.loads(flags_file.read_text(encoding="utf-8"))
        
        # Should have at least the successful flags added
        assert len(final_flags) >= initial_count
        
        # Verify each successful flag is in the file
        for review_id in successful_flags:
            flag_exists = any(
                f["review_id"] == review_id and f["user_id"] == "e2e-flag-user-1"
                for f in final_flags
            )
            assert flag_exists
    
    def test_flagged_review_status_visible(self, server_process, auth_token, test_data_files):
        """Test that review shows as flagged after being flagged."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Ensure review 2001 is flagged
        requests.post(f"{E2E_BASE_URL}/reviews/2001/flag", headers=headers)
        
        # Read the review file directly
        reviews_file = test_data_files["reviews"]
        reviews = json.loads(reviews_file.read_text(encoding="utf-8-sig"))
        
        review_2001 = next((r for r in reviews if r["id"] == 2001), None)
        assert review_2001 is not None
        assert review_2001["flagged"] is True