import pytest
from app.schemas.search import MovieSearch, MovieSearchResult
from app.schemas.movie import Movie
from datetime import date


def test_title_matches_partial_case_insensitive():
    s = MovieSearch(query="incep")
    assert s.title_matches("Inception") is True
    assert s.title_matches("the inceptionist") is True
    assert s.title_matches("Interstellar") is False


def test_genre_matches_and_normalization():
    s_any = MovieSearch(query="x")
    assert s_any.genre_matches(None) is True

    s = MovieSearch(query="x", genre=" Drama ")
    assert s.genre_matches("drama") is True
    assert s.genre_matches("DRAMA") is True
    assert s.genre_matches("Comedy") is False


def test_rating_bounds_validation_error():
    with pytest.raises(ValueError):
        MovieSearch(query="x", min_rating=8.0, max_rating=7.0)


def test_rating_matches_range():
    s = MovieSearch(query="x", min_rating=6.0, max_rating=8.0)
    assert s.rating_matches(7.0) is True
    assert s.rating_matches(5.9) is False
    assert s.rating_matches(8.1) is False


def test_search_result_total_computed():
    results = [
        Movie(id="1", title="A", description="", duration=100, genre="", release=date(2020,1,1)),
        Movie(id="2", title="B", description="", duration=90, genre="", release=date(2021,1,1)),
    ]
    res = MovieSearchResult(query=MovieSearch(query="a"), results=results)
    assert res.total == 2

