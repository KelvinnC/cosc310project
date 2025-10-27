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

# -------------------- Battle Tests --------------------
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

# -------------------- BattleCreate Tests --------------------

# def test_valid_battle_create():
#     valid_data = {
#         "review1Id": 201,
#         "review2Id": 202
#     }
#     battle_create = BattleCreate(**valid_data)
#     assert battle_create.review1Id == valid_data["review1Id"]
#     assert battle_create.review1Id != battle_create.review2Id

# def test_invalid_battle_create():
#     invalid_data = {
#         "review1Id": 201,
#         "review2Id": 201
#     }
#     with pytest.raises(ValidationError):
#         BattleCreate(**invalid_data)

# def test_missing_required_fields_battle_create():
#     with pytest.raises(ValidationError):
#         BattleCreate()

# BattleResult and BattleCreate schemas were removed; validation is handled in service layer.

