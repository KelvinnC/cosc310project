import pytest
from fastapi import HTTPException, status, Response
from datetime import datetime, date
from uuid import uuid4

from app.routers.battles import create_battle, submit_vote, get_battle
from app.schemas.battle import Battle, VoteRequest
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
def mock_jwt_payload(mock_user):
    """Mock JWT payload for testing."""
    return {
        "user_id": mock_user.id,
        "username": mock_user.username,
        "role": mock_user.role
    }

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

@pytest.fixture
def mock_response():
    """Mock FastAPI Response object."""
    return Response()


def test_create_battle_success(mocker, mock_user, mock_jwt_payload, sample_reviews, mock_battle, mock_response):
    """Test successful battle creation with Location header."""
    mocker.patch("app.routers.battles.jwt_auth_dependency", return_value=mock_jwt_payload)
    mocker.patch("app.routers.battles.get_user_by_id", return_value=mock_user)
    mocker.patch("app.routers.battles.battle_pair_selector.sample_reviews_for_battle", return_value=sample_reviews)
    mocker.patch("app.routers.battles.battle_service.create_battle", return_value=mock_battle)
    
    result = create_battle(response=mock_response, current_user=mock_jwt_payload)
    
    assert result == mock_battle
    assert result.winnerId is None
    assert mock_response.headers.get("Location") == f"/battles/{mock_battle.id}"


def test_create_battle_user_not_found(mocker, mock_response):
    """Test battle creation when user doesn't exist."""
    mock_jwt = {"user_id": "nonexistent-user", "username": "ghost", "role": "user"}
    mocker.patch("app.routers.battles.jwt_auth_dependency", return_value=mock_jwt)
    mocker.patch(
        "app.routers.battles.get_user_by_id",
        side_effect=HTTPException(status_code=404, detail="User not found")
    )
    
    with pytest.raises(HTTPException) as exc_info:
        create_battle(response=mock_response, current_user=mock_jwt)
    
    assert exc_info.value.status_code == 404


def test_create_battle_no_reviews(mocker, mock_user, mock_jwt_payload, mock_response):
    """Test when reviews are not available."""
    mocker.patch("app.routers.battles.jwt_auth_dependency", return_value=mock_jwt_payload)
    mocker.patch("app.routers.battles.get_user_by_id", return_value=mock_user)
    mocker.patch("app.services.battle_pair_selector.sample_reviews_for_battle", return_value=[])
    
    with pytest.raises(HTTPException) as exc_info:
        create_battle(response=mock_response, current_user=mock_jwt_payload)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_create_battle_no_eligible_pairs(mocker, mock_user, mock_jwt_payload, sample_reviews, mock_response):
    """Test when user has voted on all available pairs."""
    mocker.patch("app.routers.battles.jwt_auth_dependency", return_value=mock_jwt_payload)
    mocker.patch("app.routers.battles.get_user_by_id", return_value=mock_user)
    mocker.patch("app.services.battle_pair_selector.sample_reviews_for_battle", return_value=sample_reviews)
    mocker.patch(
        "app.routers.battles.battle_service.create_battle",
        side_effect=ValueError("No eligible review pair found")
    )
    
    with pytest.raises(HTTPException) as exc_info:
        create_battle(response=mock_response, current_user=mock_jwt_payload)
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_create_battle_file_error(mocker, mock_user, mock_jwt_payload, mock_response):
    """Test when reviews loading fails."""
    mocker.patch("app.routers.battles.jwt_auth_dependency", return_value=mock_jwt_payload)
    mocker.patch("app.routers.battles.get_user_by_id", return_value=mock_user)
    mocker.patch(
        "app.services.battle_pair_selector.sample_reviews_for_battle",
        side_effect=OSError("File error")
    )
    
    with pytest.raises(HTTPException) as exc_info:
        create_battle(response=mock_response, current_user=mock_jwt_payload)
    
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# POST /battles/{battle_id}/votes tests
def test_submit_vote_success(mocker, mock_user, mock_jwt_payload, mock_battle, sample_reviews):
    """Test successful vote submission."""
    mocker.patch("app.routers.battles.jwt_auth_dependency", return_value=mock_jwt_payload)
    mocker.patch("app.routers.battles.get_user_by_id", return_value=mock_user)
    mocker.patch("app.routers.battles.battle_service.get_battle_by_id", return_value=mock_battle)
    mocker.patch("app.routers.battles.battle_service.submit_battle_result", return_value=None)
    mock_increment = mocker.patch("app.routers.battles.review_service.increment_vote")
    
    # Mock get_review_by_id to return the winning review
    winning_review = sample_reviews[0]  # Review with id=1
    mocker.patch("app.routers.battles.review_service.get_review_by_id", return_value=winning_review)
    
    vote_request = VoteRequest(winnerId=1)
    result = submit_vote(battle_id=mock_battle.id, payload=vote_request, current_user=mock_jwt_payload)
    
    assert result == winning_review
    assert result.id == 1
    mock_increment.assert_called_once_with(1)


def test_submit_vote_user_not_found(mocker, mock_battle):
    """Test vote submission when user doesn't exist."""
    mock_jwt = {"user_id": "nonexistent-user", "username": "ghost", "role": "user"}
    mocker.patch("app.routers.battles.jwt_auth_dependency", return_value=mock_jwt)
    mocker.patch(
        "app.routers.battles.get_user_by_id",
        side_effect=HTTPException(status_code=404, detail="User not found")
    )
    
    vote_request = VoteRequest(winnerId=1)
    
    with pytest.raises(HTTPException) as exc_info:
        submit_vote(battle_id=mock_battle.id, payload=vote_request, current_user=mock_jwt)
    
    assert exc_info.value.status_code == 404


def test_submit_vote_battle_not_found(mocker, mock_user, mock_jwt_payload):
    """Test vote submission when battle doesn't exist."""
    mocker.patch("app.routers.battles.jwt_auth_dependency", return_value=mock_jwt_payload)
    mocker.patch("app.routers.battles.get_user_by_id", return_value=mock_user)
    mocker.patch("app.routers.battles.battle_service.get_battle_by_id", side_effect=ValueError("Battle nonexistent-battle not found"))
    
    vote_request = VoteRequest(winnerId=1)
    
    with pytest.raises(HTTPException) as exc_info:
        submit_vote(battle_id="nonexistent-battle", payload=vote_request, current_user=mock_jwt_payload)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Battle" in exc_info.value.detail
    assert "not found" in exc_info.value.detail


def test_submit_vote_invalid_winner(mocker, mock_user, mock_jwt_payload, mock_battle):
    """Test when winner is not one of the battle's reviews."""
    mocker.patch("app.routers.battles.jwt_auth_dependency", return_value=mock_jwt_payload)
    mocker.patch("app.routers.battles.get_user_by_id", return_value=mock_user)
    mocker.patch("app.routers.battles.battle_service.get_battle_by_id", return_value=mock_battle)
    mocker.patch(
        "app.routers.battles.battle_service.submit_battle_result",
        side_effect=ValueError(f"Winner 999 not in battle {mock_battle.id}")
    )
    
    vote_request = VoteRequest(winnerId=999)
    
    with pytest.raises(HTTPException) as exc_info:
        submit_vote(battle_id=mock_battle.id, payload=vote_request, current_user=mock_jwt_payload)
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_submit_vote_duplicate_vote(mocker, mock_user, mock_jwt_payload, mock_battle):
    """Test when user has already voted on this pair (409 Conflict)."""
    mocker.patch("app.routers.battles.jwt_auth_dependency", return_value=mock_jwt_payload)
    mocker.patch("app.routers.battles.get_user_by_id", return_value=mock_user)
    mocker.patch("app.routers.battles.battle_service.get_battle_by_id", return_value=mock_battle)
    mocker.patch(
        "app.routers.battles.battle_service.submit_battle_result",
        side_effect=ValueError("User has already voted on this review pair")
    )
    
    vote_request = VoteRequest(winnerId=1)
    
    with pytest.raises(HTTPException) as exc_info:
        submit_vote(battle_id=mock_battle.id, payload=vote_request, current_user=mock_jwt_payload)
    
    assert exc_info.value.status_code == 409


def test_submit_vote_increment_failure(mocker, mock_user, mock_jwt_payload, mock_battle):
    """Test when vote is recorded but review vote increment fails."""
    mocker.patch("app.routers.battles.jwt_auth_dependency", return_value=mock_jwt_payload)
    mocker.patch("app.routers.battles.get_user_by_id", return_value=mock_user)
    mocker.patch("app.routers.battles.battle_service.get_battle_by_id", return_value=mock_battle)
    mocker.patch("app.routers.battles.battle_service.submit_battle_result", return_value=None)
    mocker.patch(
        "app.routers.battles.review_service.increment_vote",
        side_effect=Exception("Review not found")
    )
    
    vote_request = VoteRequest(winnerId=1)
    
    with pytest.raises(HTTPException) as exc_info:
        submit_vote(battle_id=mock_battle.id, payload=vote_request, current_user=mock_jwt_payload)
    
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Vote recorded" in exc_info.value.detail


def test_get_battle_success(mocker, mock_battle):
    """Test successful retrieval of a battle by ID."""
    mocker.patch("app.routers.battles.battle_service.get_battle_by_id", return_value=mock_battle)
    
    result = get_battle(battle_id=mock_battle.id)
    
    assert result == mock_battle
    assert result.id == mock_battle.id
    assert result.review1Id == mock_battle.review1Id
    assert result.review2Id == mock_battle.review2Id


def test_get_battle_not_found(mocker):
    """Test retrieval when battle doesn't exist."""
    mocker.patch(
        "app.routers.battles.battle_service.get_battle_by_id",
        side_effect=ValueError("Battle nonexistent-battle not found")
    )
    
    with pytest.raises(HTTPException) as exc_info:
        get_battle(battle_id="nonexistent-battle")
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Battle" in exc_info.value.detail
    assert "not found" in exc_info.value.detail
