import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories import review_repo


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _write_json(path: Path, data):
    """Helper to write JSON data to a file."""
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8-sig")


def _read_json(path: Path):
    """Helper to read JSON data from a file."""
    return json.loads(path.read_text(encoding="utf-8-sig"))


# POST /reviews Integration Tests
def test_create_review_persists_to_file(tmp_path, monkeypatch, client):
    """Test POST /reviews creates review and persists to JSON file."""
    reviews_file = tmp_path / "reviews.json"
    _write_json(reviews_file, [])
    
    monkeypatch.setattr(review_repo, "DATA_PATH", reviews_file)
    
    payload = {
        "movieId": "movie-uuid-123",
        "authorId": "author-uuid-456",
        "rating": 4.5,
        "reviewTitle": "Great Movie",
        "reviewBody": "I really enjoyed this film. The acting was superb and the plot kept me engaged.",
        "date": "2025-11-13"
    }
    
    response = client.post("/reviews", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["movieId"] == "movie-uuid-123"
    assert data["reviewTitle"] == "Great Movie"
    assert data["flagged"] is False
    assert data["votes"] == 0
    
    # Verify persistence
    persisted_reviews = _read_json(reviews_file)
    assert len(persisted_reviews) == 1
    assert persisted_reviews[0]["id"] == 1
    assert persisted_reviews[0]["reviewTitle"] == "Great Movie"

def test_create_multiple_reviews_sequential_ids(tmp_path, monkeypatch, client):
    """Test creating multiple reviews generates sequential IDs."""
    reviews_file = tmp_path / "reviews.json"
    _write_json(reviews_file, [])
    
    monkeypatch.setattr(review_repo, "DATA_PATH", reviews_file)
    
    payloads = [
        {
            "movieId": "movie-1",
            "authorId": "author-1",
            "rating": 4.0,
            "reviewTitle": f"Review {i}",
            "reviewBody": "x" * 60,
            "date": "2025-11-13"
        }
        for i in range(1, 4)
    ]
    
    for i, payload in enumerate(payloads, start=1):
        response = client.post("/reviews", json=payload)
        assert response.status_code == 201
        assert response.json()["id"] == i
    
    persisted_reviews = _read_json(reviews_file)
    assert len(persisted_reviews) == 3
    assert [r["id"] for r in persisted_reviews] == [1, 2, 3]

def test_create_review_strips_whitespace(tmp_path, monkeypatch, client):
    """Test that title and body whitespace is stripped before persistence."""
    reviews_file = tmp_path / "reviews.json"
    _write_json(reviews_file, [])
    
    monkeypatch.setattr(review_repo, "DATA_PATH", reviews_file)
    
    payload = {
        "movieId": "   movie-123   ",
        "authorId": "author-1",
        "rating": 3.5,
        "reviewTitle": "   Spaced Title   ",
        "reviewBody": "   Body with spaces   " + ("x" * 50),
        "date": "2025-11-13"
    }
    
    response = client.post("/reviews", json=payload)
    assert response.status_code == 201
    
    persisted_reviews = _read_json(reviews_file)
    assert persisted_reviews[0]["movieId"] == "movie-123"
    assert persisted_reviews[0]["reviewTitle"] == "Spaced Title"
    assert persisted_reviews[0]["reviewBody"].startswith("Body with spaces")

# PUT /reviews Integration Tests
def test_update_review_persists_changes(tmp_path, monkeypatch, client):
    """Test PUT /reviews/{id} updates review in persistent storage."""
    reviews_file = tmp_path / "reviews.json"
    _write_json(reviews_file, [
        {
            "id": 1,
            "movieId": "movie-1",
            "authorId": "author-1",
            "rating": 3.0,
            "reviewTitle": "Original Title",
            "reviewBody": "Original body content that is long enough to pass validation requirements.",
            "flagged": False,
            "votes": 5,
            "date": "2025-11-10"
        }
    ])
    
    monkeypatch.setattr(review_repo, "DATA_PATH", reviews_file)
    
    update_payload = {
        "rating": 4.5,
        "reviewTitle": "Updated Title",
        "reviewBody": "Updated body content with new information and sufficient length for validation.",
        "flagged": False,
        "votes": 5,
        "date": "2025-11-10"
    }
    
    response = client.put("/reviews/1", json=update_payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["reviewTitle"] == "Updated Title"
    assert data["rating"] == 4.5
    assert data["movieId"] == "movie-1"  # Unchanged
    assert data["authorId"] == "author-1"  # Unchanged
    
    # Verify persistence
    persisted_reviews = _read_json(reviews_file)
    assert len(persisted_reviews) == 1
    assert persisted_reviews[0]["reviewTitle"] == "Updated Title"
    assert persisted_reviews[0]["rating"] == 4.5

def test_update_nonexistent_review_returns_404(tmp_path, monkeypatch, client):
    """Test updating non-existent review returns 404."""
    reviews_file = tmp_path / "reviews.json"
    _write_json(reviews_file, [])
    
    monkeypatch.setattr(review_repo, "DATA_PATH", reviews_file)
    
    update_payload = {
        "rating": 5.0,
        "reviewTitle": "Ghost Review",
        "reviewBody": "This review should not be created since it doesn't exist already.",
        "flagged": False,
        "votes": 0,
        "date": "2025-11-13"
    }
    
    response = client.put("/reviews/999", json=update_payload)
    
    assert response.status_code == 404
    
    # Verify no data written
    persisted_reviews = _read_json(reviews_file)
    assert len(persisted_reviews) == 0

def test_update_review_preserves_other_reviews(tmp_path, monkeypatch, client):
    """Test updating one review doesn't affect others."""
    reviews_file = tmp_path / "reviews.json"
    _write_json(reviews_file, [
        {"id": 1, "movieId": "m1", "authorId": "a1", "rating": 4.0, "reviewTitle": "Review 1", "reviewBody": "x" * 60, "flagged": False, "votes": 0, "date": "2025-11-10"},
        {"id": 2, "movieId": "m2", "authorId": "a2", "rating": 3.0, "reviewTitle": "Review 2", "reviewBody": "y" * 60, "flagged": False, "votes": 0, "date": "2025-11-11"},
        {"id": 3, "movieId": "m3", "authorId": "a3", "rating": 5.0, "reviewTitle": "Review 3", "reviewBody": "z" * 60, "flagged": False, "votes": 0, "date": "2025-11-12"},
    ])
    
    monkeypatch.setattr(review_repo, "DATA_PATH", reviews_file)
    
    update_payload = {
        "rating": 4.5,
        "reviewTitle": "Updated Review 2",
        "reviewBody": "w" * 60,
        "flagged": False,
        "votes": 0,
        "date": "2025-11-11"
    }
    
    response = client.put("/reviews/2", json=update_payload)
    assert response.status_code == 200
    
    persisted_reviews = _read_json(reviews_file)
    assert len(persisted_reviews) == 3
    assert persisted_reviews[0]["reviewTitle"] == "Review 1"  # Unchanged
    assert persisted_reviews[1]["reviewTitle"] == "Updated Review 2"  # Changed
    assert persisted_reviews[2]["reviewTitle"] == "Review 3"  # Unchanged

# DELETE /reviews Integration Tests
def test_delete_review_removes_from_file(tmp_path, monkeypatch, client):
    """Test DELETE /reviews/{id} removes review from persistent storage."""
    reviews_file = tmp_path / "reviews.json"
    _write_json(reviews_file, [
        {"id": 1, "movieId": "m1", "authorId": "a1", "rating": 4.0, "reviewTitle": "Review 1", "reviewBody": "x" * 60, "flagged": False, "votes": 0, "date": "2025-11-10"},
        {"id": 2, "movieId": "m2", "authorId": "a2", "rating": 3.0, "reviewTitle": "Review 2", "reviewBody": "y" * 60, "flagged": False, "votes": 0, "date": "2025-11-11"},
    ])
    
    monkeypatch.setattr(review_repo, "DATA_PATH", reviews_file)
    
    response = client.delete("/reviews/1")
    
    assert response.status_code == 204
    
    # Verify persistence
    persisted_reviews = _read_json(reviews_file)
    assert len(persisted_reviews) == 1
    assert persisted_reviews[0]["id"] == 2

def test_delete_nonexistent_review_returns_404(tmp_path, monkeypatch, client):
    """Test deleting non-existent review returns 404."""
    reviews_file = tmp_path / "reviews.json"
    _write_json(reviews_file, [])
    
    monkeypatch.setattr(review_repo, "DATA_PATH", reviews_file)
    
    response = client.delete("/reviews/999")
    
    assert response.status_code == 404

def test_delete_all_reviews(tmp_path, monkeypatch, client):
    """Test deleting all reviews results in empty file."""
    reviews_file = tmp_path / "reviews.json"
    _write_json(reviews_file, [
        {"id": 1, "movieId": "m1", "authorId": "a1", "rating": 4.0, "reviewTitle": "Only Review", "reviewBody": "x" * 60, "flagged": False, "votes": 0, "date": "2025-11-10"},
    ])
    
    monkeypatch.setattr(review_repo, "DATA_PATH", reviews_file)
    
    response = client.delete("/reviews/1")
    assert response.status_code == 204
    
    persisted_reviews = _read_json(reviews_file)
    assert len(persisted_reviews) == 0

# GET /reviews Integration Tests
def test_get_reviews_returns_all_persisted(tmp_path, monkeypatch, client):
    """Test GET /reviews returns all reviews from persistent storage."""
    reviews_file = tmp_path / "reviews.json"
    _write_json(reviews_file, [
        {"id": 1, "movieId": "m1", "authorId": "a1", "rating": 4.0, "reviewTitle": "Review 1", "reviewBody": "x" * 60, "flagged": False, "votes": 0, "date": "2025-11-10"},
        {"id": 2, "movieId": "m2", "authorId": "a2", "rating": 3.0, "reviewTitle": "Review 2", "reviewBody": "y" * 60, "flagged": False, "votes": 0, "date": "2025-11-11"},
    ])
    
    monkeypatch.setattr(review_repo, "DATA_PATH", reviews_file)
    
    response = client.get("/reviews")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == 1
    assert data[1]["id"] == 2

def test_get_review_by_id_from_persistent_storage(tmp_path, monkeypatch, client):
    """Test GET /reviews/{id} retrieves from persistent storage."""
    reviews_file = tmp_path / "reviews.json"
    _write_json(reviews_file, [
        {"id": 5, "movieId": "m5", "authorId": "a5", "rating": 4.5, "reviewTitle": "Specific Review", "reviewBody": "x" * 60, "flagged": False, "votes": 10, "date": "2025-11-13"},
    ])
    
    monkeypatch.setattr(review_repo, "DATA_PATH", reviews_file)
    
    response = client.get("/reviews/5")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 5
    assert data["reviewTitle"] == "Specific Review"
    assert data["votes"] == 10

# CRUD Workflow Integration Test
def test_full_crud_workflow(tmp_path, monkeypatch, client):
    """Test complete CRUD lifecycle: create -> read -> update -> delete."""
    reviews_file = tmp_path / "reviews.json"
    _write_json(reviews_file, [])
    
    monkeypatch.setattr(review_repo, "DATA_PATH", reviews_file)
    
    # 1. CREATE
    create_payload = {
        "movieId": "movie-workflow",
        "authorId": "author-workflow",
        "rating": 3.5,
        "reviewTitle": "Initial Review",
        "reviewBody": "This is the initial review body with enough content to pass validation.",
        "date": "2025-11-13"
    }
    create_response = client.post("/reviews", json=create_payload)
    assert create_response.status_code == 201
    review_id = create_response.json()["id"]
    
    # 2. READ
    read_response = client.get(f"/reviews/{review_id}")
    assert read_response.status_code == 200
    assert read_response.json()["reviewTitle"] == "Initial Review"
    
    # 3. UPDATE
    update_payload = {
        "rating": 4.5,
        "reviewTitle": "Updated Review",
        "reviewBody": "This is the updated review body with new information and sufficient length.",
        "flagged": False,
        "votes": 0,
        "date": "2025-11-13"
    }
    update_response = client.put(f"/reviews/{review_id}", json=update_payload)
    assert update_response.status_code == 200
    assert update_response.json()["reviewTitle"] == "Updated Review"
    
    # 4. DELETE
    delete_response = client.delete(f"/reviews/{review_id}")
    assert delete_response.status_code == 204
    
    # 5. VERIFY DELETION
    get_after_delete = client.get(f"/reviews/{review_id}")
    assert get_after_delete.status_code == 404
    
    # 6. VERIFY FILE IS EMPTY
    persisted_reviews = _read_json(reviews_file)
    assert len(persisted_reviews) == 0


# Data Integrity Tests
def test_create_review_with_existing_data(tmp_path, monkeypatch, client):
    """Test creating review when file already has data doesn't overwrite."""
    reviews_file = tmp_path / "reviews.json"
    _write_json(reviews_file, [
        {"id": 10, "movieId": "existing", "authorId": "a1", "rating": 5.0, "reviewTitle": "Existing", "reviewBody": "x" * 60, "flagged": False, "votes": 20, "date": "2025-11-01"},
    ])
    
    monkeypatch.setattr(review_repo, "DATA_PATH", reviews_file)
    
    payload = {
        "movieId": "new-movie",
        "authorId": "new-author",
        "rating": 4.0,
        "reviewTitle": "New Review",
        "reviewBody": "y" * 60,
        "date": "2025-11-13"
    }
    
    response = client.post("/reviews", json=payload)
    assert response.status_code == 201
    assert response.json()["id"] == 11  # Next ID after 10
    
    persisted_reviews = _read_json(reviews_file)
    assert len(persisted_reviews) == 2
    assert persisted_reviews[0]["id"] == 10  # Original preserved
    assert persisted_reviews[1]["id"] == 11  # New review added
