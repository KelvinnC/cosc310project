import json
from pathlib import Path
from app.repositories.user_repo import load_all, save_all, DATA_PATH
import datetime

def test_load_all_file_missing(mocker):
    mocker.patch.object(Path, "exists", return_value=False)
    assert load_all() == []

def test_load_all_with_data(mocker):
    mocker.patch.object(Path, "exists", return_value=True)
    payload = {
        "id": "1234",
        "username": "testmovielover",
        "hashed_password": "$2y$10$b1d2DgDhd1bdRbiwSqfZs.MhtyNCMHaYbQp3.6D3ngYLQ9ySTM/HO",
        "role": "user",
        "created_at": str(datetime.datetime.now()),
        "active": True
    }
    mock_open = mocker.patch.object(Path, "open", mocker.mock_open(read_data=json.dumps(payload)))
    result = load_all()
    assert result == payload
    mock_open.assert_called_once_with("r", encoding="utf-8")

def test_save_all_saves_data(mocker):
    users = [{
        "id": "1234",
        "username": "testmovielover",
        "hashed_password": "$2y$10$b1d2DgDhd1bdRbiwSqfZs.MhtyNCMHaYbQp3.6D3ngYLQ9ySTM/HO",
        "role": "user",
        "created_at": str(datetime.datetime.now()),
        "active": True
    }]

    mock_file = mocker.mock_open()
    mocker.patch.object(Path, "open", mock_file)

    mock_replace = mocker.patch("app.repositories.user_repo.os.replace")

    save_all(users)

    tmp_path = DATA_PATH.with_suffix(".tmp")
    mock_file.assert_called_once_with("w", encoding="utf-8")

    handle = mock_file()
    handle.write.assert_called()
    
    mock_replace.assert_called_once_with(tmp_path, DATA_PATH)