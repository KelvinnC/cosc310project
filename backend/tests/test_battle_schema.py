import pytest
from pydantic import ValidationError
from app.schemas.battle import Battle
from datetime import datetime

@pytest.fixture
def battle_data():
    payload = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "review1Id": 201,
        "review2Id": 202,
        "winnerId": None,
        "startedAt": datetime.now(),
        "endedAt": None
    }
    return payload

def test_missing_required_fields():
    with pytest.raises(ValidationError):
        Battle()

def test_valid_battle(battle_data):
    battle = Battle(**battle_data)
    assert battle.id == battle_data["id"]
    assert battle.review1Id == battle_data["review1Id"]
    assert battle.review2Id == battle_data["review2Id"]
    assert battle.winnerId is None

def test_battle_with_winner(battle_data):
    battle_data["winnerId"] = 201
    battle = Battle(**battle_data)
    assert battle.winnerId == 201


def test_battle_same_review_ids_raises_error(battle_data):
    """Test that battle with same review1Id and review2Id raises ValidationError."""
    battle_data["review1Id"] = 201
    battle_data["review2Id"] = 201  # Same as review1Id
    
    with pytest.raises(ValidationError) as exc_info:
        Battle(**battle_data)
    
    assert "Battle must have two different reviews" in str(exc_info.value)
