"""
True end-to-end tests for battle system.

These tests start the actual FastAPI server as a subprocess and make real HTTP requests,
testing the complete battle workflow including authentication, file persistence, and
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


# Test configuration
E2E_SERVER_HOST = "127.0.0.1"
E2E_SERVER_PORT = 8765
E2E_BASE_URL = f"http://{E2E_SERVER_HOST}:{E2E_SERVER_PORT}"
E2E_STARTUP_TIMEOUT = 10  # seconds
JWT_SECRET = os.environ.get("JWT_SECRET", "testsecret")


@pytest.fixture(scope="module")
def temp_data_dir():
    """Create a temporary directory for test data files."""
    temp_dir = tempfile.mkdtemp(prefix="e2e_battle_test_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="module")
def test_data_files(temp_data_dir):
    """Create test data files for users, reviews, and battles."""
    users_file = temp_data_dir / "users.json"
    reviews_file = temp_data_dir / "reviews.json"
    battles_file = temp_data_dir / "battles.json"

    # Create test users
    users_data = [
        {
            "id": "e2e-user-1",
            "username": "e2e_tester",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJz7UW2CW",  # "password"
            "role": "user",
            "created_at": datetime.now().isoformat(),
            "active": True,
            "warnings": 0
        },
        {
            "id": "e2e-user-2",
            "username": "e2e_reviewer",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJz7UW2CW",
            "role": "user",
            "created_at": datetime.now().isoformat(),
            "active": True,
            "warnings": 0
        }
    ]

    # Create test reviews (4 reviews to allow multiple battles)
    reviews_data = [
        {
            "id": 1001,
            "movieId": "e2e-movie-1",
            "authorId": "e2e-user-2",  # Not owned by e2e-user-1
            "rating": 4.5,
            "reviewTitle": "Amazing film",
            "reviewBody": "This movie was absolutely incredible. The cinematography was stunning and the acting was superb. Highly recommended for everyone.",
            "flagged": False,
            "votes": 10,
            "date": date.today().isoformat(),
            "visible": True
        },
        {
            "id": 1002,
            "movieId": "e2e-movie-1",
            "authorId": "e2e-user-2",
            "rating": 3.5,
            "reviewTitle": "Pretty good",
            "reviewBody": "Enjoyable movie with some great moments. Not perfect but definitely worth watching. The plot could have been tighter though.",
            "flagged": False,
            "votes": 5,
            "date": date.today().isoformat(),
            "visible": True
        },
        {
            "id": 1003,
            "movieId": "e2e-movie-2",
            "authorId": "e2e-user-2",
            "rating": 5.0,
            "reviewTitle": "Masterpiece",
            "reviewBody": "An absolute masterpiece that showcases the best of cinema. Every frame is carefully crafted and the story is deeply moving.",
            "flagged": False,
            "votes": 20,
            "date": date.today().isoformat(),
            "visible": True
        },
        {
            "id": 1004,
            "movieId": "e2e-movie-2",
            "authorId": "e2e-user-2",
            "rating": 4.0,
            "reviewTitle": "Solid entry",
            "reviewBody": "A solid addition to the genre with strong performances and good direction. Would watch again and recommend to friends.",
            "flagged": False,
            "votes": 15,
            "date": date.today().isoformat(),
            "visible": True
        }
    ]

    # Initially empty battles
    battles_data = []

    # Write data files
    users_file.write_text(json.dumps(users_data, indent=2), encoding="utf-8")
    reviews_file.write_text(json.dumps(reviews_data, indent=2), encoding="utf-8")
    battles_file.write_text(json.dumps(battles_data, indent=2), encoding="utf-8")

    return {
        "users": users_file,
        "reviews": reviews_file,
        "battles": battles_file
    }


@pytest.fixture(scope="module")
def auth_token():
    """Generate a valid JWT token for e2e-user-1."""
    payload = {
        "user_id": "e2e-user-1",
        "username": "e2e_tester",
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
    startup_script = temp_data_dir / "start_e2e_server.py"

    startup_script_content = f'''
import sys
sys.path.insert(0, r"{backend_dir}")

# Patch data paths before importing app
from pathlib import Path
from app.repositories import user_repo, review_repo, battle_repo

user_repo.DATA_PATH = Path(r"{test_data_files["users"]}")
review_repo.DATA_PATH = Path(r"{test_data_files["reviews"]}")
battle_repo.DATA_PATH = Path(r"{test_data_files["battles"]}")

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
    import sys
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


class TestBattleE2E:
    """End-to-end tests for battle workflow."""

    def test_server_is_running(self, server_process):
        """Verify the server is accessible."""
        response = requests.get(f"{E2E_BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["name"] == "Review Battle API"

    def test_create_battle_requires_auth(self, server_process):
        """Test that creating a battle requires authentication."""
        response = requests.post(f"{E2E_BASE_URL}/battles")
        assert response.status_code == 401

    def test_create_battle_success(self, server_process, auth_token):
        """Test successful battle creation via API."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{E2E_BASE_URL}/battles", headers=headers)

        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert "id" in data
        assert "review1Id" in data
        assert "review2Id" in data
        assert "startedAt" in data
        assert data["winnerId"] is None
        assert data["endedAt"] is None

        # Verify reviews are different
        assert data["review1Id"] != data["review2Id"]

    def test_submit_vote_success(self, server_process, auth_token, test_data_files):
        """Test submitting a vote on a battle."""
        headers = {"Authorization": f"Bearer {auth_token}"}

        # Create a battle first
        create_response = requests.post(f"{E2E_BASE_URL}/battles", headers=headers)
        assert create_response.status_code == 201
        battle_data = create_response.json()
        battle_id = battle_data["id"]
        winner_id = battle_data["review1Id"]

        # Submit vote
        vote_payload = {"winnerId": winner_id}
        vote_response = requests.post(
            f"{E2E_BASE_URL}/battles/{battle_id}/votes",
            json=vote_payload,
            headers=headers
        )

        assert vote_response.status_code == 200
        vote_data = vote_response.json()

        # Verify winning review is returned
        assert "id" in vote_data
        assert vote_data["id"] == winner_id

        # Verify battle was persisted to file
        battles_file = test_data_files["battles"]
        battles = json.loads(battles_file.read_text(encoding="utf-8"))

        saved_battle = next((b for b in battles if b["id"] == battle_id), None)
        assert saved_battle is not None
        assert saved_battle["winnerId"] == winner_id
        assert saved_battle["endedAt"] is not None
        assert saved_battle["userId"] == "e2e-user-1"

    def test_submit_vote_invalid_winner(self, server_process, auth_token):
        """Test submitting a vote with invalid winner ID."""
        headers = {"Authorization": f"Bearer {auth_token}"}

        # Create a battle
        create_response = requests.post(f"{E2E_BASE_URL}/battles", headers=headers)
        assert create_response.status_code == 201
        battle_data = create_response.json()
        battle_id = battle_data["id"]

        # Submit vote with invalid winner
        vote_payload = {"winnerId": 99999}
        vote_response = requests.post(
            f"{E2E_BASE_URL}/battles/{battle_id}/votes",
            json=vote_payload,
            headers=headers
        )

        assert vote_response.status_code == 400
        assert "not in battle" in vote_response.json()["detail"].lower()

    def test_duplicate_vote_rejected(self, server_process, auth_token):
        """Test that voting on the same pair twice is rejected."""
        headers = {"Authorization": f"Bearer {auth_token}"}

        # Create first battle and vote
        create_response1 = requests.post(f"{E2E_BASE_URL}/battles", headers=headers)
        assert create_response1.status_code == 201
        battle1 = create_response1.json()
        review1_id = battle1["review1Id"]
        review2_id = battle1["review2Id"]

        vote_payload1 = {"winnerId": review1_id}
        vote_response1 = requests.post(
            f"{E2E_BASE_URL}/battles/{battle1['id']}/votes",
            json=vote_payload1,
            headers=headers
        )
        assert vote_response1.status_code == 200

        # Try to create another battle - might get same pair
        # Keep creating until we either get the same pair or exhaust pairs
        for _ in range(10):
            create_response2 = requests.post(f"{E2E_BASE_URL}/battles", headers=headers)

            if create_response2.status_code == 201:
                battle2 = create_response2.json()

                # Check if it's the same pair (unordered)
                pair1 = frozenset([review1_id, review2_id])
                pair2 = frozenset([battle2["review1Id"], battle2["review2Id"]])

                if pair1 == pair2:
                    # This should not happen - duplicate pair
                    pytest.fail("Server created duplicate pair, should have been prevented")
                else:
                    # Vote on this new pair
                    vote_payload2 = {"winnerId": battle2["review1Id"]}
                    vote_response2 = requests.post(
                        f"{E2E_BASE_URL}/battles/{battle2['id']}/votes",
                        json=vote_payload2,
                        headers=headers
                    )
                    assert vote_response2.status_code == 200
            else:
                # Eventually should run out of pairs
                assert create_response2.status_code == 400
                assert "no eligible" in create_response2.json()["detail"].lower()
                break

    def test_multiple_battles_persistence(self, server_process, auth_token, test_data_files):
        """Test that multiple battles are correctly persisted across requests."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        battles_created = []

        # Create and vote on multiple battles (up to 6 possible pairs from 4 reviews)
        for i in range(6):
            create_response = requests.post(f"{E2E_BASE_URL}/battles", headers=headers)

            if create_response.status_code == 201:
                battle = create_response.json()
                battles_created.append(battle["id"])

                # Vote on it
                vote_payload = {"winnerId": battle["review1Id"]}
                vote_response = requests.post(
                    f"{E2E_BASE_URL}/battles/{battle['id']}/votes",
                    json=vote_payload,
                    headers=headers
                )
                assert vote_response.status_code == 200
            else:
                # Exhausted all pairs
                break

        # Verify all battles were persisted
        battles_file = test_data_files["battles"]
        battles = json.loads(battles_file.read_text(encoding="utf-8"))

        assert len(battles) >= len(battles_created)

        for battle_id in battles_created:
            saved_battle = next((b for b in battles if b["id"] == battle_id), None)
            assert saved_battle is not None
            assert saved_battle["winnerId"] is not None
            assert saved_battle["endedAt"] is not None

    def test_exhausted_pairs_returns_error(self, server_process, auth_token):
        """Test that creating battles after all pairs are voted returns an error."""
        headers = {"Authorization": f"Bearer {auth_token}"}

        # Keep creating battles until we exhaust all pairs
        max_attempts = 10
        last_response = None

        for _ in range(max_attempts):
            create_response = requests.post(f"{E2E_BASE_URL}/battles", headers=headers)

            if create_response.status_code == 201:
                battle = create_response.json()
                vote_payload = {"winnerId": battle["review1Id"]}
                requests.post(
                    f"{E2E_BASE_URL}/battles/{battle['id']}/votes",
                    json=vote_payload,
                    headers=headers
                )
            else:
                last_response = create_response
                break

        # Should eventually get an error
        assert last_response is not None
        assert last_response.status_code == 400
        assert "no eligible" in last_response.json()["detail"].lower()

    def test_battle_vote_without_auth(self, server_process):
        """Test that voting requires authentication."""
        # Try to vote without auth token
        vote_payload = {"winnerId": 1001}
        response = requests.post(
            f"{E2E_BASE_URL}/battles/some-battle-id/votes",
            json=vote_payload
        )

        assert response.status_code == 401
