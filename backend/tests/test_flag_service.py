import pytest
from datetime import datetime
from fastapi import HTTPException
from app.services import flag_service
from app.schemas.review import Review


@pytest.fixture
def mock_review():
    return Review(
        id=1,
        movieId="movie-123",
        authorId="author-456",
        rating=4.5,
        reviewTitle="Great movie",
        reviewBody="I really enjoyed this film. The acting was superb and the plot was engaging throughout.",
        flagged=False,
        votes=10,
        date="2023-01-15"
    )


@pytest.fixture
def mock_flagged_review():
    return Review(
        id=1,
        movieId="movie-123",
        authorId="author-456",
        rating=4.5,
        reviewTitle="Great movie",
        reviewBody="I really enjoyed this film. The acting was superb and the plot was engaging throughout.",
        flagged=True,
        votes=10,
        date="2023-01-15"
    )


def test_flag_review_success(mocker, mock_review):
    """Test successfully flagging a review"""
    mocker.patch("app.services.flag_service.get_review_by_id", return_value=mock_review)
    mocker.patch("app.repositories.flag_repo.load_all", return_value=[])
    mock_save = mocker.patch("app.repositories.flag_repo.save_all")
    mock_mark = mocker.patch("app.services.flag_service.mark_review_as_flagged")

    result = flag_service.flag_review(user_id="user-123", review_id=1)

    assert result["user_id"] == "user-123"
    assert result["review_id"] == 1
    assert "timestamp" in result
    mock_save.assert_called_once()
    mock_mark.assert_called_once_with(mock_review)


def test_flag_review_prevents_duplicate(mocker, mock_review):
    """Test that a user cannot flag the same review twice"""
    existing_flags = [
        {"user_id": "user-123", "review_id": 1, "timestamp": "2023-01-15T10:00:00"}
    ]
    mocker.patch("app.services.flag_service.get_review_by_id", return_value=mock_review)
    mocker.patch("app.repositories.flag_repo.load_all", return_value=existing_flags)
    mock_save = mocker.patch("app.repositories.flag_repo.save_all")

    with pytest.raises(ValueError, match="already flagged"):
        flag_service.flag_review(user_id="user-123", review_id=1)

    mock_save.assert_not_called()


def test_flag_review_different_users_can_flag(mocker, mock_review):
    """Test that different users can flag the same review"""
    existing_flags = [
        {"user_id": "user-123", "review_id": 1, "timestamp": "2023-01-15T10:00:00"}
    ]
    mocker.patch("app.services.flag_service.get_review_by_id", return_value=mock_review)
    mocker.patch("app.repositories.flag_repo.load_all", return_value=existing_flags)
    mock_save = mocker.patch("app.repositories.flag_repo.save_all")
    mock_mark = mocker.patch("app.services.flag_service.mark_review_as_flagged")

    result = flag_service.flag_review(user_id="user-456", review_id=1)

    assert result["user_id"] == "user-456"
    assert result["review_id"] == 1
    mock_save.assert_called_once()
    saved_flags = mock_save.call_args[0][0]
    assert len(saved_flags) == 2


def test_flag_review_marks_review_as_flagged(mocker, mock_review):
    """Test that flagging a review calls mark_review_as_flagged"""
    mocker.patch("app.services.flag_service.get_review_by_id", return_value=mock_review)
    mocker.patch("app.repositories.flag_repo.load_all", return_value=[])
    mocker.patch("app.repositories.flag_repo.save_all")
    mock_mark = mocker.patch("app.services.flag_service.mark_review_as_flagged")

    flag_service.flag_review(user_id="user-123", review_id=1)

    mock_mark.assert_called_once_with(mock_review)


def test_flag_review_invalid_review(mocker):
    """Test flagging a non-existent review raises HTTPException"""
    mocker.patch(
        "app.services.flag_service.get_review_by_id",
        side_effect=HTTPException(status_code=404, detail="Review not found")
    )

    with pytest.raises(HTTPException) as exc_info:
        flag_service.flag_review(user_id="user-123", review_id=999)

    assert exc_info.value.status_code == 404


def test_get_flagged_reviews_count_empty(mocker):
    """Test getting flag count when no flags exist"""
    mocker.patch("app.repositories.flag_repo.load_all", return_value=[])

    count = flag_service.get_flagged_reviews_count(review_id=1)

    assert count == 0


def test_get_flagged_reviews_count_single(mocker):
    """Test getting flag count with one flag"""
    flags = [
        {"user_id": "user-123", "review_id": 1, "timestamp": "2023-01-15T10:00:00"}
    ]
    mocker.patch("app.repositories.flag_repo.load_all", return_value=flags)

    count = flag_service.get_flagged_reviews_count(review_id=1)

    assert count == 1


def test_get_flagged_reviews_count_multiple(mocker):
    """Test getting flag count with multiple flags"""
    flags = [
        {"user_id": "user-123", "review_id": 1, "timestamp": "2023-01-15T10:00:00"},
        {"user_id": "user-456", "review_id": 1, "timestamp": "2023-01-15T11:00:00"},
        {"user_id": "user-789", "review_id": 2, "timestamp": "2023-01-15T12:00:00"}
    ]
    mocker.patch("app.repositories.flag_repo.load_all", return_value=flags)

    count = flag_service.get_flagged_reviews_count(review_id=1)

    assert count == 2


def test_get_flagged_reviews_count_different_reviews(mocker):
    """Test that count only includes flags for specified review"""
    flags = [
        {"user_id": "user-123", "review_id": 1, "timestamp": "2023-01-15T10:00:00"},
        {"user_id": "user-456", "review_id": 2, "timestamp": "2023-01-15T11:00:00"},
        {"user_id": "user-789", "review_id": 3, "timestamp": "2023-01-15T12:00:00"}
    ]
    mocker.patch("app.repositories.flag_repo.load_all", return_value=flags)

    count = flag_service.get_flagged_reviews_count(review_id=2)

    assert count == 1


def test_flag_review_verifies_collaborator_calls(mocker):
    """Test internal collaborator invocation sequence (white-box)"""
    dummy_review = {"id": 42, "flagged": False}
    mock_get = mocker.patch("app.services.flag_service.get_review_by_id", return_value=dummy_review)
    mock_load = mocker.patch("app.repositories.flag_repo.load_all", return_value=[])
    mock_save = mocker.patch("app.repositories.flag_repo.save_all")
    mock_mark = mocker.patch("app.services.flag_service.mark_review_as_flagged")

    result = flag_service.flag_review(user_id="u-1", review_id=42)

    mock_get.assert_called_once_with(42)
    mock_load.assert_called_once()
    mock_save.assert_called_once()
    mock_mark.assert_called_once_with(dummy_review)
    assert result["review_id"] == 42
    assert result["user_id"] == "u-1"


def test_get_flagged_reviews_count_cross_review_isolation(mocker):
    """Test count aggregation across distinct review IDs"""
    mocker.patch("app.repositories.flag_repo.load_all", return_value=[
        {"user_id": "u-1", "review_id": 7},
        {"user_id": "u-2", "review_id": 7},
        {"user_id": "u-3", "review_id": 8},
    ])
    assert flag_service.get_flagged_reviews_count(7) == 2
    assert flag_service.get_flagged_reviews_count(8) == 1
    assert flag_service.get_flagged_reviews_count(99) == 0


def test_unflag_review_success(mocker, mock_flagged_review):
    """Test successfully unflagging a review"""
    mocker.patch("app.services.flag_service.get_review_by_id", return_value=mock_flagged_review)
    mocker.patch("app.repositories.flag_repo.load_all", return_value=[])
    mock_save = mocker.patch("app.repositories.flag_repo.save_all")
    mock_mark = mocker.patch("app.services.flag_service.mark_review_as_unflagged")

    flag_service.unflag_review(review_id=1)

    mock_save.assert_called_once()
    mock_mark.assert_called_once_with(mock_flagged_review)


def test_unflag_review_not_found(mocker, mock_flagged_review):
    """Test unflagging a review that is not found"""
    mocker.patch("app.services.flag_service.get_review_by_id", side_effect=HTTPException(status_code=404, detail="Review Not Found"))
    mocker.patch("app.repositories.flag_repo.load_all", return_value=[])
    mock_save = mocker.patch("app.repositories.flag_repo.save_all")
    mock_mark = mocker.patch("app.services.flag_service.mark_review_as_unflagged")

    with pytest.raises(HTTPException) as ex:
        flag_service.unflag_review(review_id=123)
    assert ex.value.status_code == 404
