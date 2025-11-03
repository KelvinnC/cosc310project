import pytest

from app.schemas.search import MovieSearch
from app.services.search_service import (
    search_reviews_by_title,
    search_movies_with_reviews,
)


def _movie(id: str, title: str):
    return {
        "id": id,
        "title": title,
        "description": "",
        "duration": 120,
        "genre": "Drama",
        "release": "2019-10-04",
    }


def _review(idx: int, movie_id, rating: float = 7.5):
    return {
        "id": idx,
        "movieId": movie_id,
        "date": "2020-01-01",
        "authorId": 1,
        "reviewTitle": f"t{idx}",
        "reviewBody": f"b{idx}",
        "rating": rating,
        "votes": 0,
        "flagged": False,
    }


def test_search_reviews_by_title_uuid_ids(mocker):
    movies = [
        _movie("uuid-joker", "Joker"),
        _movie("uuid-thor", "Thor"),
    ]
    reviews = [
        _review(1, "uuid-joker"),
        _review(2, "uuid-joker"),
        _review(3, "uuid-thor"),
    ]
    mocker.patch("app.services.search_service.load_movies", return_value=movies)
    mocker.patch("app.services.search_service.load_reviews", return_value=reviews)

    res = search_reviews_by_title(MovieSearch(query="Jok"))
    assert len(res) == 2
    assert all(r.movieId == "uuid-joker" for r in res)


def test_search_reviews_by_title_legacy_integer_ids(mocker):
    movies = [
        _movie("uuid-a", "Alpha"),
        _movie("uuid-b", "Beta"),
    ]
    reviews = [
        _review(10, 1),
        _review(11, 2),
    ]
    mocker.patch("app.services.search_service.load_movies", return_value=movies)
    mocker.patch("app.services.search_service.load_reviews", return_value=reviews)

    res = search_reviews_by_title(MovieSearch(query="Bet"))
    assert len(res) == 1
    assert res[0].movieId == "uuid-b"


def test_all_matching_reviews_no_match_returns_empty(mocker):
    movies = [_movie("uuid-joker", "Joker")]
    reviews = [_review(1, "uuid-joker")]
    mocker.patch("app.services.search_service.load_movies", return_value=movies)
    mocker.patch("app.services.search_service.load_reviews", return_value=reviews)

    res = search_reviews_by_title(MovieSearch(query="Thor"))
    assert res == []


def test_search_movies_with_reviews_groups_and_shapes(mocker):
    movies = [
        _movie("uuid-joker", "Joker"),
        _movie("uuid-thor", "Thor"),
    ]
    reviews = [
        _review(1, "uuid-joker"),
        _review(2, 1),
        _review(3, "uuid-thor"),
    ]
    mocker.patch("app.services.search_service.load_movies", return_value=movies)
    mocker.patch("app.services.search_service.load_reviews", return_value=reviews)

    res = search_movies_with_reviews(MovieSearch(query="jo"))
    assert isinstance(res, list)
    assert len(res) == 1
    m = res[0]
    assert m.id == "uuid-joker"
    assert m.title == "Joker"
    assert len(m.reviews) == 2
    assert all(rv.movieId == "uuid-joker" for rv in m.reviews)


def test_search_reviews_by_title_pagination(mocker):
    movies = [_movie("uuid-joker", "Joker")]
    many_reviews = [_review(i, "uuid-joker") for i in range(1, 61)]
    mocker.patch("app.services.search_service.load_movies", return_value=movies)
    mocker.patch("app.services.search_service.load_reviews", return_value=many_reviews)

    page1 = search_reviews_by_title(MovieSearch(query="Jok"), page=1, per_page=50)
    page2 = search_reviews_by_title(MovieSearch(query="Jok"), page=2, per_page=50)

    assert len(page1) == 50
    assert len(page2) == 10
    # Ensure no overlap
    ids1 = {r.id for r in page1}
    ids2 = {r.id for r in page2}
    assert ids1.isdisjoint(ids2)

