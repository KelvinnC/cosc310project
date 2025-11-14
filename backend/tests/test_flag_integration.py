import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories import flag_repo, review_repo
from app.middleware.auth_middleware import jwt_auth_dependency


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _write_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def test_flag_review_integration_persists_and_marks_review(tmp_path, monkeypatch, client):
    """Full stack: router -> service -> repos updates both flags and review flagged state"""
    flags_file = tmp_path / "flags.json"
    reviews_file = tmp_path / "reviews.json"
    _write_json(flags_file, [])
    _write_json(reviews_file, [
        {
            "id": 1,
            "movieId": "m-1",
            "authorId": "author-1",
            "rating": 4,
            "reviewTitle": "Solid movie",
            "reviewBody": "x" * 60,
            "flagged": False,
            "votes": 0,
            "date": "2025-11-13"
        }
    ])

    # Patch repository data locations
    monkeypatch.setattr(flag_repo, "DATA_FILE", str(flags_file))
    monkeypatch.setattr(review_repo, "DATA_PATH", reviews_file)

    user = {"user_id": "user-123", "username": "tester", "role": "user"}
    app.dependency_overrides[jwt_auth_dependency] = lambda: user

    try:
        resp = client.post("/reviews/1/flag")
        assert resp.status_code == 201

        flags = json.loads(flags_file.read_text(encoding="utf-8"))
        assert len(flags) == 1
        assert flags[0]["review_id"] == 1
        assert flags[0]["user_id"] == "user-123"

        reviews = json.loads(reviews_file.read_text(encoding="utf-8-sig"))
        assert reviews[0]["flagged"] is True
    finally:
        app.dependency_overrides.clear()


def test_flag_review_integration_duplicate(tmp_path, monkeypatch, client):
    """Second flag from same user results in 409 while first persists"""
    flags_file = tmp_path / "flags.json"
    reviews_file = tmp_path / "reviews.json"
    _write_json(flags_file, [])
    _write_json(reviews_file, [
        {
            "id": 2,
            "movieId": "m-2",
            "authorId": "author-2",
            "rating": 5,
            "reviewTitle": "Great movie",
            "reviewBody": "y" * 60,
            "flagged": False,
            "votes": 0,
            "date": "2025-11-13"
        }
    ])

    monkeypatch.setattr(flag_repo, "DATA_FILE", str(flags_file))
    monkeypatch.setattr(review_repo, "DATA_PATH", reviews_file)

    user = {"user_id": "user-999", "username": "tester", "role": "user"}
    app.dependency_overrides[jwt_auth_dependency] = lambda: user

    try:
        first = client.post("/reviews/2/flag")
        assert first.status_code == 201
        second = client.post("/reviews/2/flag")
        assert second.status_code == 409

        flags = json.loads(flags_file.read_text(encoding="utf-8"))
        assert len(flags) == 1  # only one persisted
    finally:
        app.dependency_overrides.clear()
