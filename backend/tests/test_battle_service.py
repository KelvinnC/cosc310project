# test_battle_service.py
import pytest
from datetime import datetime, date
from uuid import uuid4
import random

from app.services import battle_service
from app.schemas.user import User
from app.schemas.review import Review
from app.schemas.battle import Battle


@pytest.fixture
def user():
    # Mock a user with some own reviews and some previous battle UUIDs
    return User(
        id="user1",
        username="testuser",
        hashed_password="hashed",
        role="user",
        createdAt=datetime.now(),
        ownReviewIds=[1, 2],  # user cannot battle their own reviews
        votedBattles=["battle1", "battle2"]  # previously voted battles
    )

@pytest.fixture
def reviews():
    # Create 5 reviews (IDs 1-5) for testing
    return [
        Review(
            id=i,
            movieId=1,
            authorId=100 + i,
            rating=4.5,
            reviewTitle=f"Title {i}",
            reviewBody=f"Body of review {i}",
            flagged=False,
            votes=0,
            date=date.today()
        )
        for i in range(1, 6)
    ]


def test_create_battle_excludes_own_reviews(mocker):
    # --- Setup user ---
    user = User(
        id="user1",
        username="testuser",
        hashed_password="hashed",
        role="user",
        createdAt=datetime(2025, 10, 23, 15, 13, 59, 543758),
        active=True,
        ownReviewIds=[1, 2],
        votedBattles=["battle1", "battle2"]
    )

    # --- Setup reviews ---
    reviews = [
    Review(id=1, movieId=1, authorId=101, rating=4.5, reviewTitle="Title 1", reviewBody="Body 1", flagged=False, votes=0, date=date(2025, 10, 23)),
    Review(id=2, movieId=1, authorId=101, rating=4.0, reviewTitle="Title 2", reviewBody="Body 2", flagged=False, votes=0, date=date(2025, 10, 23)),
    Review(id=3, movieId=1, authorId=102, rating=3.5, reviewTitle="Title 3", reviewBody="Body 3", flagged=False, votes=0, date=date(2025, 10, 23)),
    Review(id=4, movieId=1, authorId=103, rating=5.0, reviewTitle="Title 4", reviewBody="Body 4", flagged=False, votes=0, date=date(2025, 10, 23)),
    Review(id=5, movieId=1, authorId=104, rating=2.5, reviewTitle="Title 5", reviewBody="Body 5", flagged=False, votes=0, date=date(2025, 10, 23)),
    ]

    # --- Mock previous battles for this user ---
    previous_battles = [
        {"id": "battle1", "userId": "user1", "review1Id": 3, "review2Id": 4},
        {"id": "battle2", "userId": "user1", "review1Id": 4, "review2Id": 5},
    ]

    mocker.patch("app.repositories.battle_repo.load_all", return_value=previous_battles)
    mock_save = mocker.patch("app.repositories.battle_repo.save_all")

    # --- Patch random.choice to make the test deterministic ---
    mocker.patch("random.choice", return_value=(3, 5))

    # --- Run the function ---
    battle = battle_service.createBattle(user, reviews)

    # --- Validate results ---
    # 1. User should not battle their own reviews
    assert battle.review1Id not in user.ownReviewIds
    assert battle.review2Id not in user.ownReviewIds

    # 2. The chosen pair should not be one the user already voted on
    voted_pairs = {frozenset((b["review1Id"], b["review2Id"])) for b in previous_battles}
    assert frozenset((battle.review1Id, battle.review2Id)) not in voted_pairs

    # 3. createBattle should NOT persist the battle yet
    mock_save.assert_not_called()


def test_create_battle_no_eligible_pairs(user, reviews, mocker):
    # All eligible pairs already voted
    battle_ids = ["battle1", "battle2", "battle3"]
    previous_battles = [
        {"id": "battle1", "userId": user.id, "review1Id": 3, "review2Id": 4},
        {"id": "battle2", "userId": user.id, "review1Id": 3, "review2Id": 5},
        {"id": "battle3", "userId": user.id, "review1Id": 4, "review2Id": 5},
    ]
    # Update user's votedBattles to match the previous battles
    user.votedBattles = battle_ids
    
    mocker.patch("app.repositories.battle_repo.load_all", return_value=previous_battles)

    with pytest.raises(ValueError, match="No eligible review pairs available"):
        battle_service.createBattle(user, reviews)


def test_submit_battle_result_success(user, reviews, mocker):
    battle = Battle(
        id=str(uuid4()),
        review1Id=3,
        review2Id=4,
        startedAt=datetime.now(),
        winnerId=None,
        endedAt=None
    )
    mocker.patch("app.repositories.battle_repo.load_all", return_value=[])
    mock_save = mocker.patch("app.repositories.battle_repo.save_all")
    mock_get_user = mocker.patch("app.services.user_service.get_user_by_id", return_value=user)
    mock_update_user = mocker.patch("app.services.user_service.update_user_state")

    # Submit the vote
    battle_service.submitBattleResult(battle, winner_id=3, user_id=user.id)

    mock_save.assert_called_once()
    saved = mock_save.call_args[0][0][0]
    assert saved["winnerId"] == 3
    assert saved["endedAt"] is not None
    # User's votedBattles should have been appended and update_user_state called
    assert battle.id in user.votedBattles
    mock_update_user.assert_called_once()


def test_create_battle_single_eligible_pair(user, reviews, mocker):
    """Test battle creation when only one valid pair remains."""
    # Set user to have voted on all pairs except (3,5)
    previous_battles = [
        {"id": "battle1", "userId": user.id, "review1Id": 3, "review2Id": 4},
        {"id": "battle2", "userId": user.id, "review1Id": 4, "review2Id": 5},
    ]
    user.votedBattles = ["battle1", "battle2"]
    mocker.patch("app.repositories.battle_repo.load_all", return_value=previous_battles)
    mock_save = mocker.patch("app.repositories.battle_repo.save_all")
    
    battle = battle_service.createBattle(user, reviews)
    
    # Should select the only remaining pair (3,5)
    assert frozenset((battle.review1Id, battle.review2Id)) == frozenset((3, 5))
    # createBattle should NOT persist the battle yet
    mock_save.assert_not_called()

def test_create_battle_all_reviews_owned(user, reviews, mocker):
    """Test when all available reviews are owned by the user."""
    user.ownReviewIds = [r.id for r in reviews]  # User owns all reviews
    mocker.patch("app.repositories.battle_repo.load_all", return_value=[])
    
    with pytest.raises(ValueError, match="No eligible review pairs available"):
        battle_service.createBattle(user, reviews)

def test_create_battle_empty_reviews(user, mocker):
    """Test battle creation with empty review pool."""
    mocker.patch("app.repositories.battle_repo.load_all", return_value=[])
    
    with pytest.raises(ValueError, match="No eligible review pairs available"):
        battle_service.createBattle(user, [])

def test_submit_battle_result_invalid_winner(user, mocker):
    """Submitting a winner that's not part of the battle should raise."""
    battle = Battle(
        id=str(uuid4()),
        review1Id=3,
        review2Id=4,
        startedAt=datetime.now(),
        winnerId=None,
        endedAt=None,
    )

    with pytest.raises(ValueError, match="Winner .* not in battle"):
        battle_service.submitBattleResult(battle, winner_id=99, user_id=user.id)

def test_submit_battle_result_marks_end_time(user, mocker):
    """Test that submitting result properly sets endedAt timestamp."""
    # Create a Battle object and assert saved dict contains winner/endedAt
    battle = Battle(
        id=str(uuid4()),
        review1Id=3,
        review2Id=4,
        startedAt=datetime.now(),
        winnerId=None,
        endedAt=None,
    )
    mocker.patch("app.repositories.battle_repo.load_all", return_value=[])
    mock_save = mocker.patch("app.repositories.battle_repo.save_all")
    mocker.patch("app.services.user_service.get_user_by_id", return_value=user)
    mocker.patch("app.services.user_service.update_user_state")

    battle_service.submitBattleResult(battle, winner_id=3, user_id=user.id)

    # Verify battle was updated with end time and winner
    updated_battle = mock_save.call_args[0][0][0]
    assert updated_battle["endedAt"] is not None
    assert updated_battle["winnerId"] == 3
