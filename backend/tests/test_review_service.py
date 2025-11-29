import pytest
import datetime
from fastapi import HTTPException
from app.services.review_service import create_review, update_review, get_review_by_id, list_reviews, delete_review, increment_vote, get_reviews_by_author
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
        "rating": 5.0,
        "reviewTitle": "good movie",
        "reviewBody": "I absolutely loved this movie! The cinematography was stunning and the plot kept me engaged throughout.",
        "flagged": False,
        "votes": 5,
        "date": "2022-01-01"
    }])
    reviews = list_reviews()
    assert reviews[0].id == 1
    assert reviews[0].movieId == "1234"
    assert reviews[0].authorId == -1
    assert reviews[0].rating == 5.0
    assert reviews[0].reviewTitle == "good movie"
    assert reviews[0].reviewBody == "I absolutely loved this movie! The cinematography was stunning and the plot kept me engaged throughout."
    assert reviews[0].flagged == False
    assert reviews[0].votes == 5
    assert reviews[0].date == datetime.date(2022, 1, 1)
    assert len(reviews) == 1

@pytest.mark.asyncio
async def test_create_review_adds_review(mocker):
    mocker.patch("app.services.review_service.load_all", return_value=[])
    mock_save = mocker.patch("app.services.review_service.save_all")
    mocker.patch("app.repositories.movie_repo.load_all", return_value=[{"id": "UUID-movie-5678"}])
    # Empty store -> next integer ID should be 1
    payload = ReviewCreate(
        movieId="UUID-movie-5678", rating=5.0, reviewTitle="good movie", reviewBody="I absolutely loved this movie! The cinematography was stunning and the plot kept me engaged throughout."
    )

    review = await create_review(payload, author_id="UUID-author-5678")

    assert review.id == 1
    assert review.movieId == "UUID-movie-5678"
    assert review.authorId == "UUID-author-5678"
    assert review.rating == 5.0
    assert review.reviewTitle == "good movie"
    assert review.reviewBody == "I absolutely loved this movie! The cinematography was stunning and the plot kept me engaged throughout."
    assert review.flagged == False
    assert isinstance(review.date, datetime.date)
    assert mock_save.called

@pytest.mark.asyncio
async def test_create_review_collides_id(mocker):
    # If existing reviews contain id 1234, next id should be 1235
    mocker.patch("app.services.review_service.load_all", return_value=[
    {
        "id": 1234,
        "movieId": "UUID-movie-1234",
        "authorId": "UUID-author-1234",
        "rating": 5.0,
        "reviewTitle": "good movie",
        "reviewBody": "I absolutely loved this movie! The cinematography was stunning and the plot kept me engaged throughout.",
        "flagged": False,
        "votes": 5,
        "date": "2022-01-01"
    }])
    mock_save = mocker.patch("app.services.review_service.save_all")
    mocker.patch("app.repositories.movie_repo.load_all", return_value=[{"id": "1234"}])
    payload = ReviewCreate(movieId="1234", rating=5.0, reviewTitle="good movie", reviewBody="I absolutely loved this movie! The cinematography was stunning and the plot kept me engaged throughout.")

    review = await create_review(payload, author_id="UUID-author-1234")
    assert review.id == 1235
    assert mock_save.called

@pytest.mark.asyncio
async def test_create_review_strips_whitespace(mocker):
    mocker.patch("app.services.review_service.load_all", return_value=[])
    mock_save = mocker.patch("app.services.review_service.save_all")
    mocker.patch("uuid.uuid4", return_value="1234")
    mocker.patch("app.repositories.movie_repo.load_all", return_value=[{"id": "1234"}])
    payload = ReviewCreate(
        movieId="    1234       ", rating=5.0, reviewTitle="      good movie    ", reviewBody="   I absolutely loved this movie! The cinematography was stunning and the plot kept me engaged throughout.   "
    )
    review = await create_review(payload, author_id="UUID-author-5678")
    assert review.movieId == "1234"
    assert review.authorId == "UUID-author-5678"
    assert review.reviewTitle == "good movie"
    assert mock_save.called

def test_get_review_by_id_valid_id(mocker):
    mocker.patch("app.services.review_service.load_all", return_value=[
    {
        "id": 1234,
        "movieId": "1234",
        "authorId": 1234,
        "rating": 5.0,
        "reviewTitle": "good movie",
        "reviewBody": "I absolutely loved this movie! The cinematography was stunning and the plot kept me engaged throughout.",
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
        "rating": 5.0,
        "reviewTitle": "good movie",
        "reviewBody": "I absolutely loved this movie! The cinematography was stunning and the plot kept me engaged throughout.",
        "flagged": False,
        "votes": 5,
        "date": "2022-01-01"
    }])
    mock_save = mocker.patch("app.services.review_service.save_all")
    from app.schemas.review import ReviewUpdate
    payload = ReviewUpdate(rating=5.0, reviewTitle="Updated Test", reviewBody="I absolutely hated this movie! The cinematography was terrible and the plot kept me confused throughout.", flagged=False, votes=5, date="2022-01-01")
    review = update_review(1234, payload)
    assert review.rating == 5.0
    assert review.reviewTitle == "Updated Test"
    assert review.reviewBody == "I absolutely hated this movie! The cinematography was terrible and the plot kept me confused throughout."
    assert mock_save.called

def test_update_review_invalid_id(mocker):
    mocker.patch("app.services.review_service.load_all", return_value=[])
    mock_save = mocker.patch("app.services.review_service.save_all")
    from app.schemas.review import ReviewUpdate
    payload = ReviewUpdate(rating=5.0, reviewTitle="good movie", reviewBody="I absolutely loved this movie! The cinematography was stunning and the plot kept me engaged throughout.", flagged=False, votes=5, date="2022-01-01")
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
        "rating": 5.0,
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

def test_increment_vote_successful(mocker):
    """Test incrementing votes on an existing review."""
    review_data = {
        "id": 1234,
        "movieId": "movie-uuid",
        "authorId": "author-uuid",
        "rating": 4.5,
        "reviewTitle": "Great movie",
        "reviewBody": "Really enjoyed it",
        "flagged": False,
        "votes": 10,
        "date": "2022-01-01"
    }
    mocker.patch("app.services.review_service.load_all", return_value=[review_data])
    mock_save = mocker.patch("app.services.review_service.save_all")
    
    increment_vote(1234)
    
    # Verify save was called
    assert mock_save.called
    # Verify the vote count was incremented
    saved_reviews = mock_save.call_args[0][0]
    assert saved_reviews[0]["votes"] == 11

def test_increment_vote_from_zero(mocker):
    """Test incrementing votes when initial count is 0."""
    review_data = {
        "id": 5678,
        "movieId": "movie-uuid",
        "authorId": "author-uuid",
        "rating": 3.0,
        "reviewTitle": "Okay movie",
        "reviewBody": "It was fine",
        "flagged": False,
        "votes": 0,
        "date": "2023-01-01"
    }
    mocker.patch("app.services.review_service.load_all", return_value=[review_data])
    mock_save = mocker.patch("app.services.review_service.save_all")
    
    increment_vote(5678)
    
    saved_reviews = mock_save.call_args[0][0]
    assert saved_reviews[0]["votes"] == 1

def test_increment_vote_missing_votes_field(mocker):
    """Test incrementing votes when votes field is missing (defaults to 0)."""
    review_data = {
        "id": 9999,
        "movieId": "movie-uuid",
        "authorId": "author-uuid",
        "rating": 5.0,
        "reviewTitle": "Amazing",
        "reviewBody": "Best ever",
        "flagged": False,
        "date": "2024-01-01"
        # votes field intentionally missing
    }
    mocker.patch("app.services.review_service.load_all", return_value=[review_data])
    mock_save = mocker.patch("app.services.review_service.save_all")
    
    increment_vote(9999)
    
    saved_reviews = mock_save.call_args[0][0]
    assert saved_reviews[0]["votes"] == 1

def test_increment_vote_review_not_found(mocker):
    """Test incrementing votes for non-existent review raises 404."""
    mocker.patch("app.services.review_service.load_all", return_value=[])
    
    with pytest.raises(HTTPException) as ex:
        increment_vote(99999)
    
    assert ex.value.status_code == 404
    assert "not found" in ex.value.detail.lower()

def test_increment_vote_multiple_reviews(mocker):
    """Test incrementing votes only affects the target review."""
    reviews = [
        {"id": 1, "movieId": "m1", "authorId": "a1", "rating": 4.0, "reviewTitle": "Good", "reviewBody": "Nice", "flagged": False, "votes": 5, "date": "2022-01-01"},
        {"id": 2, "movieId": "m2", "authorId": "a2", "rating": 3.0, "reviewTitle": "Ok", "reviewBody": "Fine", "flagged": False, "votes": 3, "date": "2022-02-01"},
        {"id": 3, "movieId": "m3", "authorId": "a3", "rating": 5.0, "reviewTitle": "Great", "reviewBody": "Best", "flagged": False, "votes": 15, "date": "2022-03-01"}
    ]
    mocker.patch("app.services.review_service.load_all", return_value=reviews)
    mock_save = mocker.patch("app.services.review_service.save_all")
    
    increment_vote(2)
    
    saved_reviews = mock_save.call_args[0][0]
    # Only review 2 should be incremented
    assert saved_reviews[0]["votes"] == 5  # unchanged
    assert saved_reviews[1]["votes"] == 4  # incremented
    assert saved_reviews[2]["votes"] == 15  # unchanged

def test_get_review_by_author_id(mocker):
    mocker.patch("app.services.review_service.load_all", return_value=[
    {
        "id":  7777,
        "movieId":  "asdfsesfsesfe",
        "date":  "2010-08-31",
        "authorId":  "test_id",
        "reviewTitle":  "Good Movie",
        "reviewBody":  "this is a review body",
        "rating":  4.5,
        "votes":  6,
        "flagged":  False
    }])
    reviews = get_reviews_by_author("test_id")
    assert reviews[0].id == 7777
    assert reviews[0].movieId == "asdfsesfsesfe"
    assert reviews[0].reviewTitle == "Good Movie"
    assert reviews[0].reviewBody == "this is a review body"
    assert reviews[0].rating == 4.5
    assert reviews[0].votes == 6
    assert reviews[0].flagged == False
    assert isinstance(reviews[0], Review)