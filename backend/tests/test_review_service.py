import pytest
import datetime
from fastapi import HTTPException
from app.services.review_service import create_review, update_review, get_review_by_id, list_reviews, delete_review
from app.schemas.review import ReviewCreate, Review

def test_list_review_empty_list(mocker):
    mocker.patch("app.services.review_service.load_all", return_value=[])
    reviews = list_reviews()
    assert reviews == []

def test_list_review_has_reviews(mocker):
    mocker.patch("app.services.review_service.load_all", return_value=[
    {
        "id": 1,
        "movieId": "1234",
        "authorId": -1,
        "rating": 5.5,
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "flagged": False,
        "votes": 5,
        "date": "2022-01-01"
    }])
    reviews = list_reviews()
    assert reviews[0].id == 1
    assert reviews[0].movieId == "1234"
    assert reviews[0].authorId == -1
    assert reviews[0].rating == 5.5
    assert reviews[0].reviewTitle == "good movie"
    assert reviews[0].reviewBody == "loved the movie"
    assert reviews[0].flagged == False
    assert reviews[0].votes == 5
    assert reviews[0].date == datetime.date(2022, 1, 1)
    assert len(reviews) == 1

def test_create_review_adds_review(mocker):
    mocker.patch("app.services.review_service.load_all", return_value=[])
    mock_save = mocker.patch("app.services.review_service.save_all")
    # Empty store -> next integer ID should be 1
    payload = ReviewCreate(
        movieId="1234", authorId=1234, rating=5.5, reviewTitle="good movie", reviewBody="loved the movie", date="2022-01-01"
    )

    review = create_review(payload)

    assert review.id == 1
    assert review.movieId == "1234"
    assert review.authorId == 1234
    assert review.rating == 5.5
    assert review.reviewTitle == "good movie"
    assert review.reviewBody == "loved the movie"
    assert review.flagged == False
    assert review.date == datetime.date(2022, 1, 1)
    assert mock_save.called

def test_create_review_collides_id(mocker):
    # If existing reviews contain id 1234, next id should be 1235
    mocker.patch("app.services.review_service.load_all", return_value=[
    {
        "id": 1234,
        "movieId": "1234",
        "authorId": 1234,
        "rating": 5.5,
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "flagged": False,
        "votes": 5,
        "date": "2022-01-01"
    }])
    mock_save = mocker.patch("app.services.review_service.save_all")
    payload = ReviewCreate(movieId="1234", authorId=1234, rating=5.5, reviewTitle="good movie", reviewBody="loved the movie", date="2022-01-01")

    review = create_review(payload)
    assert review.id == 1235
    assert mock_save.called

def test_create_review_strips_whitespace(mocker):
    mocker.patch("app.services.review_service.load_all", return_value=[])
    mock_save = mocker.patch("app.services.review_service.save_all")
    mocker.patch("uuid.uuid4", return_value="1234")
    payload = ReviewCreate(
        movieId="    1234       ", authorId=1234, rating=5.5, reviewTitle="      good movie    ", reviewBody="loved the movie", flagged=False, votes=5, date="2022-01-01"
    )
    review = create_review(payload)
    assert review.movieId == "1234"
    assert review.authorId == 1234
    assert review.reviewTitle == "good movie"
    assert mock_save.called

def test_get_review_by_id_valid_id(mocker):
    mocker.patch("app.services.review_service.load_all", return_value=[
    {
        "id": 1234,
        "movieId": "1234",
        "authorId": 1234,
        "rating": 5.5,
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "flagged": False,
        "votes": 5,
        "date": "2022-01-01"
    }])
    review = get_review_by_id(1234)
    assert review.id == 1234
    assert review.movieId == "1234"
    assert isinstance(review, Review)

def test_get_review_by_id_invalid_id(mocker):
    mocker.patch("app.services.review_service.load_all", return_value=[])
    with pytest.raises(HTTPException) as ex:
        get_review_by_id(1234)
    assert ex.value.status_code == 404
    assert "not found" in ex.value.detail

def test_update_review_valid_update(mocker):
    mocker.patch("app.services.review_service.load_all", return_value=[
    {
        "id": 1234,
        "movieId": "1234",
        "authorId": 1234,
        "rating": 5.5,
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "flagged": False,
        "votes": 5,
        "date": "2022-01-01"
    }])
    mock_save = mocker.patch("app.services.review_service.save_all")
    from app.schemas.review import ReviewUpdate
    payload = ReviewUpdate(rating=7.7, reviewTitle="Updated Test", reviewBody="hated the movie", flagged=False, votes=5, date="2022-01-01")
    review = update_review(1234, payload)
    assert review.rating == 7.7
    assert review.reviewTitle == "Updated Test"
    assert review.reviewBody == "hated the movie"
    assert mock_save.called

def test_update_review_invalid_id(mocker):
    mocker.patch("app.services.review_service.load_all", return_value=[])
    mock_save = mocker.patch("app.services.review_service.save_all")
    from app.schemas.review import ReviewUpdate
    payload = ReviewUpdate(rating=5.5, reviewTitle="good movie", reviewBody="loved the movie", flagged=False, votes=5, date="2022-01-01")
    with pytest.raises(HTTPException) as ex:
        update_review(1234, payload)
    assert ex.value.status_code == 404
    assert "not found" in ex.value.detail

def test_delete_review_valid_review(mocker):
    mocker.patch("app.services.review_service.load_all", return_value=[
    {
        "id": 1234,
        "movieId": "1234",
        "authorId": 1234,
        "rating": 5.5,
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "flagged": False,
        "votes": 5,
        "date": "2022-01-01"
    }])
    mock_save = mocker.patch("app.services.review_service.save_all")
    delete_review(1234)
    saved_reviews = mock_save.call_args[0][0]
    assert all(m['id'] != 1234 for m in saved_reviews)
    assert mock_save.called

def test_delete_review_invalid_review(mocker):
    mocker.patch("app.services.review_service.load_all", return_value=[])
    mock_save = mocker.patch("app.services.review_service.save_all")
    with pytest.raises(HTTPException) as ex:
        delete_review(1234)
    assert ex.value.status_code == 404
    assert "not found" in ex.value.detail