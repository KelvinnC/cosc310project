import pytest
from app.services import flag_service


def test_flag_review_calls_mark_review_as_flagged(mocker):
    # Arrange
    dummy_review = {"id": 42, "flagged": False}
    mock_get = mocker.patch("app.services.flag_service.get_review_by_id", return_value=dummy_review)
    mock_load = mocker.patch("app.repositories.flag_repo.load_all", return_value=[])
    mock_save = mocker.patch("app.repositories.flag_repo.save_all")
    mock_mark = mocker.patch("app.services.flag_service.mark_review_as_flagged")

    # Act
    result = flag_service.flag_review(user_id="u-1", review_id=42)

    # Assert
    mock_get.assert_called_once_with(42)
    mock_load.assert_called_once()
    mock_save.assert_called_once()
    mock_mark.assert_called_once_with(dummy_review)
    assert result["review_id"] == 42
    assert result["user_id"] == "u-1"


def test_flag_review_prevents_duplicate(mocker):
    existing = [{"user_id": "u-1", "review_id": 42, "timestamp": "2025-11-13T10:00:00"}]
    mocker.patch("app.services.flag_service.get_review_by_id", return_value={"id": 42})
    mocker.patch("app.repositories.flag_repo.load_all", return_value=existing)

    with pytest.raises(ValueError):
        flag_service.flag_review(user_id="u-1", review_id=42)


def test_flag_review_allows_different_user(mocker):
    existing = [{"user_id": "u-1", "review_id": 42, "timestamp": "2025-11-13T10:00:00"}]
    mocker.patch("app.services.flag_service.get_review_by_id", return_value={"id": 42})
    mocker.patch("app.repositories.flag_repo.load_all", return_value=existing)
    mock_save = mocker.patch("app.repositories.flag_repo.save_all")
    mock_mark = mocker.patch("app.services.flag_service.mark_review_as_flagged")

    result = flag_service.flag_review(user_id="u-2", review_id=42)

    mock_save.assert_called_once()
    mock_mark.assert_called_once()
    assert result["user_id"] == "u-2"


def test_get_flagged_reviews_count_empty(mocker):
    mocker.patch("app.repositories.flag_repo.load_all", return_value=[])
    assert flag_service.get_flagged_reviews_count(99) == 0


def test_get_flagged_reviews_count_multiple(mocker):
    mocker.patch("app.repositories.flag_repo.load_all", return_value=[
        {"user_id": "u-1", "review_id": 7},
        {"user_id": "u-2", "review_id": 7},
        {"user_id": "u-3", "review_id": 8},
    ])
    assert flag_service.get_flagged_reviews_count(7) == 2
    assert flag_service.get_flagged_reviews_count(8) == 1
