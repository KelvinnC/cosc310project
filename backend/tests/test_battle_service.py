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
    # Mock a user with a UUID4 id (string)
    return User(
        id="123e4567-e89b-12d3-a456-426614174000",
        username="testuser",
        hashed_password="hashed",
        role="user",
        created_at=datetime.now(),
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


## ------------- createBattle tests ------------- ##

def test_create_battle_excludes_own_reviews(mocker):
    # --- Setup user ---
    user = User(
        id="123e4567-e89b-12d3-a456-426614174000",
        username="testuser",
        hashed_password="hashed",
        role="user",
        created_at=datetime(2025, 10, 23, 15, 13, 59, 543758),
        active=True,
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
        {"id": "battle1", "userId": user.id, "review1Id": 3, "review2Id": 4, "winnerId": 3},
        {"id": "battle2", "userId": user.id, "review1Id": 4, "review2Id": 5, "winnerId": 4},
    ]

    mocker.patch("app.repositories.battle_repo.load_all", return_value=previous_battles)
    mock_save = mocker.patch("app.repositories.battle_repo.save_all")

    # --- Patch random.choice to make the test deterministic ---
    mocker.patch("random.choice", return_value=(3, 5))

    # Simulate that reviews with ids 1 and 2 are owned by the user
    mocker.patch("app.services.battle_service._is_own_review", side_effect=lambda u, r: r.id in {1,2})

    # --- Run the function ---
    battle = battle_service.createBattle(user, reviews)

    # --- Validate results ---
    # 1. User should not battle their own reviews (ids 1 and 2 marked as owned)
    assert battle.review1Id not in {1,2}
    assert battle.review2Id not in {1,2}

    # 2. The chosen pair should not be one the user already voted on
    voted_pairs = {frozenset((b["review1Id"], b["review2Id"])) for b in previous_battles}
    assert frozenset((battle.review1Id, battle.review2Id)) not in voted_pairs

    # 3. createBattle should NOT persist the battle yet
    mock_save.assert_not_called()


def test_create_battle_no_eligible_pairs(user, reviews, mocker):
    # All eligible pairs already voted
    previous_battles = [
        {"id": "battle1", "userId": user.id, "review1Id": 3, "review2Id": 4, "winnerId": 3},
        {"id": "battle2", "userId": user.id, "review1Id": 3, "review2Id": 5, "winnerId": 3},
        {"id": "battle3", "userId": user.id, "review1Id": 4, "review2Id": 5, "winnerId": 4},
    ]
    # Mark reviews 1 and 2 as owned to leave only 3,4,5 eligible
    mocker.patch("app.services.battle_service._is_own_review", side_effect=lambda u, r: r.id in {1,2})
    
    mocker.patch("app.repositories.battle_repo.load_all", return_value=previous_battles)

    with pytest.raises(ValueError, match="No eligible review pairs available"):
        battle_service.createBattle(user, reviews)


def test_create_battle_single_eligible_pair(user, reviews, mocker):
    """Test battle creation when only one valid pair remains."""
    # Set user to have voted on all pairs except (3,5)
    previous_battles = [
        {"id": "battle1", "userId": user.id, "review1Id": 3, "review2Id": 4, "winnerId": 3},
        {"id": "battle2", "userId": user.id, "review1Id": 4, "review2Id": 5, "winnerId": 5},
    ]
    mocker.patch("app.services.battle_service._is_own_review", side_effect=lambda u, r: r.id in {1,2})
    mocker.patch("app.repositories.battle_repo.load_all", return_value=previous_battles)
    mock_save = mocker.patch("app.repositories.battle_repo.save_all")
    
    battle = battle_service.createBattle(user, reviews)
    
    # Should select the only remaining pair (3,5)
    assert frozenset((battle.review1Id, battle.review2Id)) == frozenset((3, 5))
    # createBattle should NOT persist the battle yet
    mock_save.assert_not_called()

def test_create_battle_all_reviews_owned(user, reviews, mocker):
    """Test when all available reviews are owned by the user."""
    mocker.patch("app.services.battle_service._is_own_review", return_value=True)
    mocker.patch("app.repositories.battle_repo.load_all", return_value=[])
    
    with pytest.raises(ValueError, match="No eligible review pairs available"):
        battle_service.createBattle(user, reviews)

def test_create_battle_empty_reviews(user, mocker):
    """Test battle creation with empty review pool."""
    mocker.patch("app.repositories.battle_repo.load_all", return_value=[])
    
    with pytest.raises(ValueError, match="No eligible review pairs available"):
        battle_service.createBattle(user, [])


