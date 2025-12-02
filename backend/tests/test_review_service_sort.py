import pytest
from app.services.review_service import list_reviews


def test_list_reviews_no_sort_returns_models_and_does_not_mutate(mocker):
    data = [
        {"id": 1, "movieId": "A", "rating": 4.0, "authorId": 1, "reviewTitle": "t", "reviewBody": "b", "date": "2020-01-01"},
        {"id": 2, "movieId": "B", "rating": 5.0, "authorId": 1, "reviewTitle": "t", "reviewBody": "b", "date": "2020-01-02"},
    ]
    mocker.patch("app.services.review_service.load_all", return_value=data)
    result = list_reviews()
    assert [r.id for r in result] == [1, 2]
    assert [r.movieId for r in result] == ["A", "B"]
    # Original list contents are unchanged (no in-place modification)
    assert data[0]["id"] == 1 and data[1]["id"] == 2


def test_filter_by_rating_exact_match(mocker):
    data = [
        {"id": 1, "movieId": "A", "rating": 5, "authorId": 1, "reviewTitle": "t", "reviewBody": "b", "date": "2020-01-01"},
        {"id": 2, "movieId": "B", "rating": "5.0", "authorId": 1, "reviewTitle": "t", "reviewBody": "b", "date": "2020-01-02"},
        {"id": 3, "movieId": "C", "rating": 4.0, "authorId": 1, "reviewTitle": "t", "reviewBody": "b", "date": "2020-01-03"},
        {"id": 4, "movieId": "D", "authorId": 1, "reviewTitle": "t", "reviewBody": "b", "date": "2020-01-04"},
    ]
    mocker.patch("app.services.review_service.load_all", return_value=data)
    only_fives = list_reviews(rating=5)
    assert [r.id for r in only_fives] == [1, 2]


def test_sort_by_rating_ascending_descending(mocker):
    data = [
        {"id": 1, "movieId": "A", "rating": 3.0, "authorId": 1, "reviewTitle": "t", "reviewBody": "b", "date": "2020-01-01"},
        {"id": 2, "movieId": "B", "rating": "4.5", "authorId": 1, "reviewTitle": "t", "reviewBody": "b", "date": "2020-01-02"},
        {"id": 3, "movieId": "C", "rating": 0, "authorId": 1, "reviewTitle": "t", "reviewBody": "b", "date": "2020-01-03"},
        {"id": 4, "movieId": "D", "rating": 5.0, "authorId": 1, "reviewTitle": "t", "reviewBody": "b", "date": "2020-01-04"},
    ]
    mocker.patch("app.services.review_service.load_all", return_value=data)

    asc = list_reviews(sort_by="rating", order="asc")
    assert [r.id for r in asc] == [3, 1, 2, 4]
    desc = list_reviews(sort_by="rating", order="desc")
    assert [r.id for r in desc] == [4, 2, 1, 3]

    # Original list reference is unchanged (no in-place modification)
    assert data[0]["id"] == 1 and data[1]["id"] == 2 and data[2]["id"] == 3 and data[3]["id"] == 4


def test_sort_by_movie_id_supports_uuid_and_index(mocker):
    reviews = [
        {"id": 1, "movieId": 1, "rating": 3.0, "authorId": 1, "reviewTitle": "t", "reviewBody": "b", "date": "2020-01-01"},
        {"id": 2, "movieId": "C", "rating": 4.0, "authorId": 1, "reviewTitle": "t", "reviewBody": "b", "date": "2020-01-02"},
        {"id": 3, "movieId": "B", "rating": 2.0, "authorId": 1, "reviewTitle": "t", "reviewBody": "b", "date": "2020-01-03"},
        {"id": 4, "movieId": 99, "rating": 5.0, "authorId": 1, "reviewTitle": "t", "reviewBody": "b", "date": "2020-01-04"},
    ]
    movies = [
        {"id": "A", "title": "Zeta"},
        {"id": "B", "title": "Alpha"},
        {"id": "C", "title": "Omega"},
    ]
    mocker.patch("app.services.review_service.load_all", return_value=reviews)
    mocker.patch("app.repositories.movie_repo.load_all", return_value=movies)

    asc = list_reviews(sort_by="movieId", order="asc")
    assert [r.id for r in asc] == [1, 4, 3, 2]

    desc = list_reviews(sort_by="movieId", order="desc")
    assert [r.id for r in desc] == [2, 3, 1, 4]


def test_sort_by_movie_title_ascending_descending(mocker):
    reviews = [
        {"id": 1, "movieId": "A", "rating": 3.0, "authorId": 1, "reviewTitle": "t", "reviewBody": "b", "date": "2020-01-01"},
        {"id": 2, "movieId": 2, "rating": 4.0, "authorId": 1, "reviewTitle": "t", "reviewBody": "b", "date": "2020-01-02"},
        {"id": 3, "movieId": "C", "rating": 2.0, "authorId": 1, "reviewTitle": "t", "reviewBody": "b", "date": "2020-01-03"},
        {"id": 4, "movieId": 99, "rating": 5.0, "authorId": 1, "reviewTitle": "t", "reviewBody": "b", "date": "2020-01-04"},
    ]
    movies = [
        {"id": "A", "title": "Zeta"},
        {"id": "B", "title": "Alpha"},
        {"id": "C", "title": "Omega"},
    ]
    mocker.patch("app.services.review_service.load_all", return_value=reviews)
    mocker.patch("app.repositories.movie_repo.load_all", return_value=movies)

    asc = list_reviews(sort_by="movieTitle", order="asc")
    assert [r.id for r in asc] == [2, 4, 3, 1]

    desc = list_reviews(sort_by="movieTitle", order="desc")
    assert [r.id for r in desc] == [1, 3, 2, 4]
