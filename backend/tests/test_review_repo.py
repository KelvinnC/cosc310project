import pytest
import json
from pathlib import Path
from app.repositories.review_repo import get_all_reviews, load_all, save_all, DATA_PATH

def test_get_all_reviews_returns_copy_when_no_filter_or_sort(mocker):
    data = [
        {"id": 1, "movieId": "A", "rating": 4.0},
        {"id": 2, "movieId": "B", "rating": 5.0},
    ]
    mocker.patch("app.repositories.review_repo.load_all", return_value=data)
    result = get_all_reviews()
    assert result == data
    assert result is not data


def test_filter_by_rating_exact_match(mocker):
    data = [
        {"id": 1, "movieId": "A", "rating": 5},
        {"id": 2, "movieId": "B", "rating": "5.0"},
        {"id": 3, "movieId": "C", "rating": 4.0},
        {"id": 4, "movieId": "D"},
    ]
    mocker.patch("app.repositories.review_repo.load_all", return_value=data)
    only_fives = get_all_reviews(rating=5)
    assert [r["id"] for r in only_fives] == [1, 2]


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
