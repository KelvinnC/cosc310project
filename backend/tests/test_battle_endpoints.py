# test_battle_endpoints.py
"""Tests for battles router endpoints."""
import pytest
from fastapi import HTTPException, status
from datetime import datetime, date
from uuid import uuid4

from app.routers.battles import create_battle, submit_vote
from app.schemas.battle import Battle, BattleResult
from app.schemas.user import User
from app.schemas.review import Review


@pytest.fixture
def mock_user():
    """Mock user for testing."""
    return User(
        id="test-user-uuid-123",
        username="testuser",
        hashed_password="hashed_password_123",
        role="user",
        created_at=datetime.now(),
        active=True
    )

@pytest.fixture
def sample_reviews():
    """Sample reviews for testing."""
    return [
        Review(
            id=i,
            movieId="movie-uuid-1",
            authorId=f"author-{i}",
            rating=4.0 + (i * 0.1),
            reviewTitle=f"Review Title {i}",
            reviewBody=f"This is the body of review {i}",
            flagged=False,
            votes=i * 10,
            date=date.today()
        )
        for i in range(1, 11)
    ]

@pytest.fixture
def mock_battle():
    """Mock battle object."""
    return Battle(
        id=str(uuid4()),
        review1Id=1,
        review2Id=2,
        winnerId=None,
        startedAt=datetime.now(),
        endedAt=None
    )


# POST /{user_id}/create tests
def test_create_battle_success(mocker, mock_user, sample_reviews, mock_battle):
    """Test successful battle creation."""
    mocker.patch("app.routers.battles.get_user_by_id", return_value=mock_user)
    mocker.patch("app.routers.battles._sample_reviews_for_battle", return_value=sample_reviews)
    mocker.patch("app.routers.battles.battle_service.createBattle", return_value=mock_battle)
    
    result = create_battle(user_id=mock_user.id)
    
    assert result == mock_battle
    assert result.winnerId is None


def test_create_battle_user_not_found(mocker):
    """Test battle creation when user doesn't exist."""
    mocker.patch(
        "app.routers.battles.get_user_by_id",
        side_effect=HTTPException(status_code=404, detail="User not found")
    )
    
    with pytest.raises(HTTPException) as exc_info:
        create_battle(user_id="nonexistent-user")
    
    assert exc_info.value.status_code == 404


def test_create_battle_no_reviews(mocker, mock_user):
    """Test when reviews are not available."""
    mocker.patch("app.routers.battles.get_user_by_id", return_value=mock_user)
    mocker.patch("app.routers.battles._sample_reviews_for_battle", return_value=[])
    
    with pytest.raises(HTTPException) as exc_info:
        create_battle(user_id=mock_user.id)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_create_battle_no_eligible_pairs(mocker, mock_user, sample_reviews):
    """Test when user has voted on all available pairs."""
    mocker.patch("app.routers.battles.get_user_by_id", return_value=mock_user)
    mocker.patch("app.routers.battles._sample_reviews_for_battle", return_value=sample_reviews)
    mocker.patch(
        "app.routers.battles.battle_service.createBattle",
        side_effect=ValueError("No eligible review pairs available for this user.")
    )
    
    with pytest.raises(HTTPException) as exc_info:
        create_battle(user_id=mock_user.id)
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_create_battle_file_error(mocker, mock_user):
    """Test when reviews loading fails."""
    mocker.patch("app.routers.battles.get_user_by_id", return_value=mock_user)
    mocker.patch(
        "app.routers.battles._sample_reviews_for_battle",
        side_effect=Exception("File error")
    )
    
    with pytest.raises(HTTPException) as exc_info:
        create_battle(user_id=mock_user.id)
    
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# POST /{user_id}/vote tests
def test_submit_vote_success(mocker, mock_user, mock_battle):
    """Test successful vote submission."""
    mocker.patch("app.routers.battles.get_user_by_id", return_value=mock_user)
    mocker.patch("app.routers.battles.battle_service.submitBattleResult", return_value=None)
    
    battle_result = BattleResult(battle=mock_battle, winnerId=1)
    result = submit_vote(user_id=mock_user.id, payload=battle_result)
    
    assert result is None


def test_submit_vote_user_not_found(mocker, mock_battle):
    """Test vote submission when user doesn't exist."""
    mocker.patch(
        "app.routers.battles.get_user_by_id",
        side_effect=HTTPException(status_code=404, detail="User not found")
    )
    
    battle_result = BattleResult(battle=mock_battle, winnerId=1)
    
    with pytest.raises(HTTPException) as exc_info:
        submit_vote(user_id="nonexistent-user", payload=battle_result)
    
    assert exc_info.value.status_code == 404


def test_submit_vote_invalid_winner(mocker, mock_user, mock_battle):
    """Test when winner is not one of the battle's reviews."""
    mocker.patch("app.routers.battles.get_user_by_id", return_value=mock_user)
    mocker.patch(
        "app.routers.battles.battle_service.submitBattleResult",
        side_effect=ValueError(f"Winner 999 not in battle {mock_battle.id}")
    )
    
    battle_result = BattleResult(battle=mock_battle, winnerId=999)
    
    with pytest.raises(HTTPException) as exc_info:
        submit_vote(user_id=mock_user.id, payload=battle_result)
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_submit_vote_duplicate_vote(mocker, mock_user, mock_battle):
    """Test when user has already voted on this pair (409 Conflict)."""
    mocker.patch("app.routers.battles.get_user_by_id", return_value=mock_user)
    mocker.patch(
        "app.routers.battles.battle_service.submitBattleResult",
        side_effect=ValueError("User has already voted on this review pair")
    )
    
    battle_result = BattleResult(battle=mock_battle, winnerId=1)
    
    with pytest.raises(HTTPException) as exc_info:
        submit_vote(user_id=mock_user.id, payload=battle_result)
    
    assert exc_info.value.status_code == 409
