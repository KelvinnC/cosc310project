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

def test_add_movie_to_user_watchlist(mocker):
    mock_save = mocker.patch(
        "app.services.watchlist_service.save_all",
    )
    
    updated_watchlist = add_movie_to_user_watchlist(101, "movie-4")
    
    assert updated_watchlist.authorId == 101
    assert "movie-4" in updated_watchlist.movieIds
    mock_save.assert_called_once()
    saved_data = mock_save.call_args[0][0]
    assert any(w for w in saved_data if w["authorId"] == 101 and "movie-4" in w["movieIds"])               