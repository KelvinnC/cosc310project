import pytest
import json
from pathlib import Path
from app.repositories.review_repo import load_all, save_all, DATA_PATH



def test_load_all_file_missing(mocker):
    mocker.patch.object(Path, "exists", return_value=False)
    assert load_all() == []


def test_load_all_with_data(mocker):
    mocker.patch.object(Path, "exists", return_value=True)
    payload = [{
        "id": "1234",
        "movieId": "1234",
        "authorId": "1234",
        "rating": "5.5",
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "flagged": "False",
        "votes": 5,
        "date": "2022-01-01"
    }]
    mock_open = mocker.patch.object(Path, "open", mocker.mock_open(read_data=json.dumps(payload)))
    result = load_all()
    assert result == payload
    mock_open.assert_called_once_with("r", encoding="utf-8-sig")


def test_save_all_saves_data(mocker):
    reviews = [{
        "id": "1234",
        "movieId": "1234",
        "authorId": "1234",
        "rating": "5.5",
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "flagged": "False",
        "votes": 5,
        "date": "2022-01-01"
    }]

    mock_file = mocker.mock_open()
    mocker.patch.object(Path, "open", mock_file)

    mock_replace = mocker.patch("app.repositories.review_repo.os.replace")

    save_all(reviews)

    tmp_path = DATA_PATH.with_suffix(".tmp")
    mock_file.assert_called_once_with("w", encoding="utf-8-sig")

    handle = mock_file()
    handle.write.assert_called()

    mock_replace.assert_called_once_with(tmp_path, DATA_PATH)
