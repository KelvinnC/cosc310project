"""
Tests for TMDb service
"""
import pytest
from unittest.mock import patch, AsyncMock
from app.services.tmdb_service import (
    is_tmdb_movie_id,
    extract_tmdb_id,
    create_tmdb_movie_id,
    search_tmdb_movies,
    get_tmdb_movie_details
)


def test_is_tmdb_movie_id():
    assert is_tmdb_movie_id("tmdb_12345") is True
    assert is_tmdb_movie_id("tmdb_27205") is True
    assert is_tmdb_movie_id("550e8400-e29b-41d4-a716-446655440000") is False
    assert is_tmdb_movie_id("12345") is False


def test_extract_tmdb_id():
    assert extract_tmdb_id("tmdb_12345") == 12345
    assert extract_tmdb_id("tmdb_27205") == 27205
    assert extract_tmdb_id("invalid") is None
    assert extract_tmdb_id("tmdb_invalid") is None


def test_create_tmdb_movie_id():
    assert create_tmdb_movie_id(12345) == "tmdb_12345"
    assert create_tmdb_movie_id(27205) == "tmdb_27205"


@pytest.mark.asyncio
@patch("app.services.tmdb_service.TMDB_API_KEY", "test_key")
async def test_search_tmdb_movies(mocker):
    # Mock TMDb API response
    from unittest.mock import Mock
    mock_response = Mock()
    mock_response.json.return_value = {
        "results": [
            {
                "id": 27205,
                "title": "Inception",
                "overview": "A thief who steals corporate secrets...",
                "release_date": "2010-07-15",
                "poster_path": "/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg"
            }
        ]
    }
    mock_response.raise_for_status = Mock()
    
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    
    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    
    results = await search_tmdb_movies("Inception")
    
    assert len(results) == 1
    assert results[0]["tmdb_id"] == 27205
    assert results[0]["title"] == "Inception"


@pytest.mark.asyncio
@patch("app.services.tmdb_service.TMDB_API_KEY", "test_key")
async def test_get_tmdb_movie_details(mocker):
    # Mock TMDb API response
    from unittest.mock import Mock
    mock_response = Mock()
    mock_response.json.return_value = {
        "id": 27205,
        "title": "Inception",
        "overview": "A thief who steals corporate secrets...",
        "runtime": 148,
        "release_date": "2010-07-15",
        "genres": [{"name": "Action"}, {"name": "Sci-Fi"}],
        "poster_path": "/poster.jpg",
        "backdrop_path": "/backdrop.jpg"
    }
    mock_response.raise_for_status = Mock()
    
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    
    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    
    result = await get_tmdb_movie_details(27205)
    
    assert result["tmdb_id"] == 27205
    assert result["title"] == "Inception"
    assert result["duration"] == 148
    assert result["genre"] == "Action, Sci-Fi"
