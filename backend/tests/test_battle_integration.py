"""
Integration tests for the battle workflow.

Tests the full end-to-end flow: battle creation → voting → persistence → state changes
using real file I/O (similar to test_flag_integration.py).
"""
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from datetime import date

from app.main import app
from app.repositories import battle_repo, review_repo, user_repo
from app.middleware.auth_middleware import jwt_auth_dependency


@pytest.fixture
def client():
    """FastAPI test client."""
    with TestClient(app) as c:
        yield c


def _write_json(path: Path, data):
    """Helper to write JSON data to a file."""
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_json(path: Path):
    """Helper to read JSON data from a file."""
    return json.loads(path.read_text(encoding="utf-8-sig"))


@pytest.fixture
def setup_test_data(tmp_path, monkeypatch):
    """Set up temporary test data files and patch repository paths."""
    battles_file = tmp_path / "battles.json"
    reviews_file = tmp_path / "reviews.json"
    users_file = tmp_path / "users.json"
    
    # User data
    users_data = [
        {
            "id": "test-user-123",
            "username": "tester",
            "hashed_password": "hashed_password",
            "role": "user",
            "created_at": "2025-11-01T10:00:00",
            "active": True,
            "warnings": 0
        },
        {
            "id": "author-1",
            "username": "author1",
            "hashed_password": "hashed_password",
            "role": "user",
            "created_at": "2025-11-01T10:00:00",
            "active": True,
            "warnings": 0
        },
        {
            "id": "author-2",
            "username": "author2",
            "hashed_password": "hashed_password",
            "role": "user",
            "created_at": "2025-11-01T10:00:00",
            "active": True,
            "warnings": 0
        },
        {
            "id": "author-3",
            "username": "author3",
            "hashed_password": "hashed_password",
            "role": "user",
            "created_at": "2025-11-01T10:00:00",
            "active": True,
            "warnings": 0
        }
    ]
    
    # Initial test data
    reviews_data = [
        {
            "id": 1,
            "movieId": "movie-uuid-1",
            "authorId": "author-1",
            "rating": 4.5,
            "reviewTitle": "Great movie",
            "reviewBody": "This movie was absolutely fantastic and I loved every minute of it.",
            "flagged": False,
            "votes": 10,
            "date": "2025-11-01",
            "visible": True
        },
        {
            "id": 2,
            "movieId": "movie-uuid-1",
            "authorId": "author-2",
            "rating": 3.5,
            "reviewTitle": "Decent film",
            "reviewBody": "It was okay, had some good moments but also some slow parts overall.",
            "flagged": False,
            "votes": 5,
            "date": "2025-11-02",
            "visible": True
        },
        {
            "id": 3,
            "movieId": "movie-uuid-2",
            "authorId": "author-3",
            "rating": 5.0,
            "reviewTitle": "Masterpiece",
            "reviewBody": "An absolute masterpiece that will be remembered for generations to come.",
            "flagged": False,
            "votes": 20,
            "date": "2025-11-03",
            "visible": True
        },
        {
            "id": 4,
            "movieId": "movie-uuid-2",
            "authorId": "test-user-123",
            "rating": 4.0,
            "reviewTitle": "My review",
            "reviewBody": "This is my own review and should not appear in my battles at all.",
            "flagged": False,
            "votes": 0,
            "date": "2025-11-04",
            "visible": True
        }
    ]
    
    _write_json(battles_file, [])
    _write_json(reviews_file, reviews_data)
    _write_json(users_file, users_data)
    
    # Patch repository paths
    monkeypatch.setattr(battle_repo, "DATA_PATH", battles_file)
    monkeypatch.setattr(review_repo, "DATA_PATH", reviews_file)
    monkeypatch.setattr(user_repo, "DATA_PATH", users_file)
    
    return {
        "battles_file": battles_file,
        "reviews_file": reviews_file,
        "users_file": users_file,
        "reviews_data": reviews_data,
        "users_data": users_data
    }


def test_battle_creation_and_vote_workflow(setup_test_data, client):
    """
    Full workflow: Create battle → Submit vote → Verify persistence and vote increment.
    """
    battles_file = setup_test_data["battles_file"]
    reviews_file = setup_test_data["reviews_file"]
    
    # Mock authenticated user
    user = {"user_id": "test-user-123", "username": "tester", "role": "user"}
    app.dependency_overrides[jwt_auth_dependency] = lambda: user
    
    try:
        # Step 1: Create a battle
        create_resp = client.post("/battles")
        assert create_resp.status_code == 201
        battle = create_resp.json()
        assert "id" in battle
        assert "review1Id" in battle
        assert "review2Id" in battle
        assert battle["winnerId"] is None
        battle_id = battle["id"]
        review1_id = battle["review1Id"]
        review2_id = battle["review2Id"]
        
        # Verify battle doesn't include user's own review (id=4)
        assert review1_id != 4 and review2_id != 4
        
        # Verify battle was persisted
        battles = _read_json(battles_file)
        assert len(battles) == 1
        assert battles[0]["id"] == battle_id
        assert battles[0]["winnerId"] is None
        
        # Step 2: Submit a vote
        vote_payload = {"winnerId": review1_id}
        vote_resp = client.post(f"/battles/{battle_id}/votes", json=vote_payload)
        assert vote_resp.status_code == 200
        
        # Step 3: Verify battle was updated with winner
        battles_after_vote = _read_json(battles_file)
        assert len(battles_after_vote) == 1
        voted_battle = battles_after_vote[0]
        assert voted_battle["winnerId"] == review1_id
        assert voted_battle["endedAt"] is not None
        
        # Step 4: Verify winning review vote count was incremented
        reviews_after_vote = _read_json(reviews_file)
        winning_review = next(r for r in reviews_after_vote if r["id"] == review1_id)
        original_review = next(r for r in setup_test_data["reviews_data"] if r["id"] == review1_id)
        assert winning_review["votes"] == original_review["votes"] + 1
        
        # Step 5: Verify losing review vote count unchanged
        losing_review = next(r for r in reviews_after_vote if r["id"] == review2_id)
        original_losing = next(r for r in setup_test_data["reviews_data"] if r["id"] == review2_id)
        assert losing_review["votes"] == original_losing["votes"]
        
    finally:
        app.dependency_overrides.clear()


def test_multiple_battles_track_voted_pairs(setup_test_data, client):
    """
    Create multiple battles and verify voted pairs are tracked correctly.
    """
    battles_file = setup_test_data["battles_file"]
    
    user = {"user_id": "test-user-123", "username": "tester", "role": "user"}
    app.dependency_overrides[jwt_auth_dependency] = lambda: user
    
    try:
        voted_pairs = set()
        
        # Create 3 battles and vote on each
        for i in range(3):
            # Create battle
            create_resp = client.post("/battles")
            assert create_resp.status_code == 201
            battle = create_resp.json()
            
            # Track the pair
            pair = frozenset((battle["review1Id"], battle["review2Id"]))
            assert pair not in voted_pairs, f"Duplicate pair generated: {pair}"
            voted_pairs.add(pair)
            
            # Vote on the battle
            vote_payload = {"winnerId": battle["review1Id"]}
            vote_resp = client.post(f"/battles/{battle['id']}/votes", json=vote_payload)
            assert vote_resp.status_code == 200
        
        # Verify all 3 battles are persisted
        battles = _read_json(battles_file)
        assert len(battles) == 3
        
        # Verify no duplicate pairs
        persisted_pairs = set()
        for b in battles:
            pair = frozenset((b["review1Id"], b["review2Id"]))
            assert pair not in persisted_pairs, "Duplicate pair found in persistence"
            persisted_pairs.add(pair)
        
    finally:
        app.dependency_overrides.clear()


def test_exhausted_pairs_returns_error(setup_test_data, client):
    """
    User votes on all possible pairs → Verify 'no eligible pairs' error on next battle.
    """
    user = {"user_id": "test-user-123", "username": "tester", "role": "user"}
    app.dependency_overrides[jwt_auth_dependency] = lambda: user
    
    try:
        # With reviews 1, 2, 3 (excluding user's review 4), there are only 3 possible pairs:
        # (1,2), (1,3), (2,3)
        
        # Vote on all 3 possible pairs
        for _ in range(3):
            create_resp = client.post("/battles")
            assert create_resp.status_code == 201
            battle = create_resp.json()
            
            vote_payload = {"winnerId": battle["review1Id"]}
            vote_resp = client.post(f"/battles/{battle['id']}/votes", json=vote_payload)
            assert vote_resp.status_code == 200
        
        # Try to create a 4th battle - should fail
        create_resp = client.post("/battles")
        assert create_resp.status_code == 400
        assert "no eligible" in create_resp.json()["detail"].lower()
        
    finally:
        app.dependency_overrides.clear()


def test_battle_lifecycle_state_changes(setup_test_data, client):
    """
    Test battle state changes: creation → retrieval → vote → retrieval.
    """
    user = {"user_id": "test-user-123", "username": "tester", "role": "user"}
    app.dependency_overrides[jwt_auth_dependency] = lambda: user
    
    try:
        # Create battle
        create_resp = client.post("/battles")
        assert create_resp.status_code == 201
        battle = create_resp.json()
        battle_id = battle["id"]
        
        # Retrieve battle before voting
        get_resp1 = client.get(f"/battles/{battle_id}")
        assert get_resp1.status_code == 200
        battle_before = get_resp1.json()
        assert battle_before["winnerId"] is None
        assert battle_before["endedAt"] is None
        assert battle_before["startedAt"] is not None
        
        # Submit vote
        vote_payload = {"winnerId": battle["review1Id"]}
        vote_resp = client.post(f"/battles/{battle_id}/votes", json=vote_payload)
        assert vote_resp.status_code == 200
        
        # Retrieve battle after voting
        get_resp2 = client.get(f"/battles/{battle_id}")
        assert get_resp2.status_code == 200
        battle_after = get_resp2.json()
        assert battle_after["winnerId"] == battle["review1Id"]
        assert battle_after["endedAt"] is not None
        assert battle_after["startedAt"] == battle_before["startedAt"]
        
    finally:
        app.dependency_overrides.clear()


def test_duplicate_vote_is_rejected(setup_test_data, client):
    """
    Verify that attempting to vote twice on the same battle pair is rejected.
    """
    battles_file = setup_test_data["battles_file"]
    
    user = {"user_id": "test-user-123", "username": "tester", "role": "user"}
    app.dependency_overrides[jwt_auth_dependency] = lambda: user
    
    try:
        # Create and vote on first battle
        create_resp = client.post("/battles")
        assert create_resp.status_code == 201
        battle1 = create_resp.json()
        
        vote_payload = {"winnerId": battle1["review1Id"]}
        vote_resp = client.post(f"/battles/{battle1['id']}/votes", json=vote_payload)
        assert vote_resp.status_code == 200
        
        # Manually create a duplicate battle with the same pair
        battles = _read_json(battles_file)
        duplicate_battle = {
            "id": "duplicate-battle-id",
            "review1Id": battle1["review1Id"],
            "review2Id": battle1["review2Id"],
            "winnerId": None,
            "userId": "test-user-123",
            "startedAt": "2025-11-17T10:00:00",
            "endedAt": None
        }
        battles.append(duplicate_battle)
        _write_json(battles_file, battles)
        
        # Try to vote on the duplicate - should fail
        vote_resp2 = client.post(f"/battles/duplicate-battle-id/votes", json=vote_payload)
        assert vote_resp2.status_code == 409
        assert "already voted" in vote_resp2.json()["detail"].lower()
        
    finally:
        app.dependency_overrides.clear()


def test_invalid_winner_is_rejected(setup_test_data, client):
    """
    Verify that voting for a review not in the battle is rejected.
    """
    user = {"user_id": "test-user-123", "username": "tester", "role": "user"}
    app.dependency_overrides[jwt_auth_dependency] = lambda: user
    
    try:
        # Create battle
        create_resp = client.post("/battles")
        assert create_resp.status_code == 201
        battle = create_resp.json()
        
        # Try to vote for a review that's not in this battle
        invalid_review_id = 999
        vote_payload = {"winnerId": invalid_review_id}
        vote_resp = client.post(f"/battles/{battle['id']}/votes", json=vote_payload)
        assert vote_resp.status_code == 400
        assert "not in battle" in vote_resp.json()["detail"].lower()
        
    finally:
        app.dependency_overrides.clear()


def test_battle_excludes_user_own_reviews(setup_test_data, client):
    """
    Verify that battles never include reviews authored by the user.
    """
    user = {"user_id": "test-user-123", "username": "tester", "role": "user"}
    app.dependency_overrides[jwt_auth_dependency] = lambda: user
    
    try:
        # Create multiple battles
        for _ in range(3):
            create_resp = client.post("/battles")
            assert create_resp.status_code == 201
            battle = create_resp.json()
            
            # Review with id=4 belongs to test-user-123
            assert battle["review1Id"] != 4, "Battle included user's own review"
            assert battle["review2Id"] != 4, "Battle included user's own review"
        
    finally:
        app.dependency_overrides.clear()
