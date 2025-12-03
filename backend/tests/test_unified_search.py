"""
Tests for unified search service
"""
import pytest
from unittest.mock import patch, AsyncMock
from app.services.unified_search_service import search_all_movies
from app.schemas.movie import MovieSummary


@pytest.mark.asyncio
@patch("app.services.unified_search_service.search_movies_titles")
@patch("app.services.unified_search_service.search_tmdb_movies")
async def test_search_with_many_local_results(mock_tmdb, mock_local):
    """When 3+ local results exist, don't query TMDb"""
    # Mock 3 local results
    mock_local.return_value = [
        MovieSummary(id="1", title="Inception Documentary"),
        MovieSummary(id="2", title="Inception Behind the Scenes"),
        MovieSummary(id="3", title="Inception Explained"),
    ]

    result = await search_all_movies("inception")

    assert len(result["local"]) == 3
    assert len(result["external"]) == 0
    assert result["source"] == "local"
    mock_tmdb.assert_not_called()


@pytest.mark.asyncio
@patch("app.services.unified_search_service.search_movies_titles")
@patch("app.services.unified_search_service.search_tmdb_movies")
async def test_search_with_few_local_results(mock_tmdb, mock_local):
    """When < 3 local results, also query TMDb"""
    # Mock 1 local result
    mock_local.return_value = [
        MovieSummary(id="1", title="Inception Documentary"),
    ]

    # Mock TMDb results
    mock_tmdb.return_value = [
        {
            "tmdb_id": 27205,
            "title": "Inception",
            "overview": "A thief...",
            "release_date": "2010-07-15",
            "poster_path": "/poster.jpg"
        }
    ]

    result = await search_all_movies("inception")

    assert len(result["local"]) == 1
    assert len(result["external"]) == 1
    assert result["source"] == "both"
    assert result["external"][0]["movie_id"] == "tmdb_27205"
    mock_tmdb.assert_called_once()


@pytest.mark.asyncio
@patch("app.services.unified_search_service.search_movies_titles")
@patch("app.services.unified_search_service.search_tmdb_movies")
async def test_search_with_no_local_results(mock_tmdb, mock_local):
    """When 0 local results, only return TMDb results"""
    # Mock no local results
    mock_local.return_value = []

    # Mock TMDb results
    mock_tmdb.return_value = [
        {
            "tmdb_id": 27205,
            "title": "Inception",
            "overview": "A thief...",
            "release_date": "2010-07-15",
            "poster_path": "/poster.jpg"
        }
    ]

    result = await search_all_movies("inception")

    assert len(result["local"]) == 0
    assert len(result["external"]) == 1
    assert result["source"] == "tmdb"


@pytest.mark.asyncio
@patch("app.services.unified_search_service.search_movies_titles")
@patch("app.services.unified_search_service.search_tmdb_movies")
async def test_search_tmdb_failure_returns_local_only(mock_tmdb, mock_local):
    """If TMDb fails, still return local results"""
    # Mock local results
    mock_local.return_value = [
        MovieSummary(id="1", title="Inception Documentary"),
    ]

    # Mock TMDb failure
    mock_tmdb.side_effect = Exception("TMDb API error")

    result = await search_all_movies("inception")

    assert len(result["local"]) == 1
    assert len(result["external"]) == 0
    assert result["source"] == "local"


@pytest.mark.asyncio
async def test_search_empty_query():
    """Empty query returns empty results"""
    result = await search_all_movies("")

    assert len(result["local"]) == 0
    assert len(result["external"]) == 0
    assert result["source"] == "local"
