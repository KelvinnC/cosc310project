# test_battle_repo.py
import json
from pathlib import Path
import datetime
import pytest
from app.repositories import battle_repo
from app.repositories.battle_repo import load_all, save_all, DATA_PATH

def test_load_all_file_missing(mocker):
    mocker.patch.object(Path, "exists", return_value=False)
    assert load_all() == []

def test_load_all_with_data(mocker):
    mocker.patch.object(Path, "exists", return_value=True)
    
    payload = [
        {
            "id": "battle123",
            "userId": "user1",
            "review1Id": 10,
            "review2Id": 20,
            "winnerId": None,
            "startedAt": str(datetime.datetime.now()),
            "endedAt": None
        }
    ]
    
    mock_open = mocker.patch.object(Path, "open", mocker.mock_open(read_data=json.dumps(payload)))
    
    result = load_all()
    assert result == payload
    mock_open.assert_called_once_with("r", encoding="utf-8")

def test_save_all_saves_data(mocker):
    battles = [
        {
            "id": "battle123",
            "userId": "user1",
            "review1Id": 10,
            "review2Id": 20,
            "winnerId": None,
            "startedAt": str(datetime.datetime.now()),
            "endedAt": None
        }
    ]

    # Patch open
    mock_file = mocker.mock_open()
    mocker.patch.object(Path, "open", mock_file)

    # Patch os.replace
    mock_replace = mocker.patch("app.repositories.battle_repo.os.replace")

    save_all(battles)

    tmp_path = DATA_PATH.with_suffix(".tmp")
    mock_file.assert_called_once_with("w", encoding="utf-8")

    handle = mock_file()
    handle.write.assert_called()

    mock_replace.assert_called_once_with(tmp_path, DATA_PATH)
