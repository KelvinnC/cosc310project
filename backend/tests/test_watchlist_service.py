import pytest
from app.services.watchlist_service import get_watchlist_by_author_id, add_movie_to_user_watchlist


def test_get_watchlist_by_author_id(mocker):
    mock_watchlists = [
        {"id": 1, "authorId": 101, "movieIds": ["movie-1", "movie-2"]},
        {"id": 2, "authorId": 102, "movieIds": ["movie-3"]},
    ]

    mocker.patch(
        "app.services.watchlist_service.load_all",
        return_value=mock_watchlists,
    )

    watchlist = get_watchlist_by_author_id(101)
    assert watchlist.authorId == 101
    assert watchlist.movieIds == ["movie-1", "movie-2"]


def test_get_watchlist_by_author_id_invalid_id(mocker):
    mock_watchlists = [
        {"id": 1, "authorId": 101, "movieIds": ["movie-1", "movie-2"]},
        {"id": 2, "authorId": 102, "movieIds": ["movie-3"]},
    ]

    mocker.patch(
        "app.services.watchlist_service.load_all",
        return_value=mock_watchlists,
    )

    watchlist = get_watchlist_by_author_id(999)
    assert watchlist is None


def test_add_movie_to_user_watchlist_valid_id(mocker):
    mock_save = mocker.patch(
        "app.services.watchlist_service.save_all",
    )

    updated_watchlist = add_movie_to_user_watchlist(101, "6bca4027-ad52-414e-810c-b830571cc07d")

    assert updated_watchlist.authorId == 101
    assert "6bca4027-ad52-414e-810c-b830571cc07d" in updated_watchlist.movieIds
    mock_save.assert_called_once()
    saved_data = mock_save.call_args[0][0]
    assert any(w for w in saved_data if w["authorId"] == 101 and "6bca4027-ad52-414e-810c-b830571cc07d" in w["movieIds"])


def test_add_movie_to_user_watchlist_invalid_id(mocker):
    mocker.patch(
        "app.services.watchlist_service.load_all_movies",
        return_value=[{"id": "movie-1"}, {"id": "movie-2"}],
    )

    with pytest.raises(Exception) as exc_info:
        add_movie_to_user_watchlist(101, "invalid-movie-id")

    assert "Movie with id 'invalid-movie-id' does not exist" in str(exc_info.value)
