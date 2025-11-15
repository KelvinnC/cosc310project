from app.services.admin_review_service import get_flagged_reviews, hide_review
from app.schemas.review import Review

def test_get_flagged_reviews_no_reviews(mocker):
    mocker.patch("app.services.admin_review_service.list_reviews", return_value=[])
    result = get_flagged_reviews()
    assert len(result) == 0

def test_get_flagged_reviews_has_flagged(mocker):
    flagged_review = [Review(**{
        "id": 1,
        "movieId": "1234",
        "authorId": -1,
        "rating": 5.5,
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "flagged": True,
        "votes": 5,
        "date": "2022-01-01"
    })]
    mocker.patch("app.services.admin_review_service.list_reviews", return_value=flagged_review)
    result = get_flagged_reviews()
    assert len(result) == 1
    assert all([review.flagged for review in result])

def test_get_flagged_reviews_has_flagged_and_unflagged(mocker):
    flagged_review = [Review(**{
        "id": 1,
        "movieId": "1234",
        "authorId": -1,
        "rating": 5.5,
        "reviewTitle": "good movie",
        "reviewBody": "loved the movie",
        "flagged": True,
        "votes": 5,
        "date": "2022-01-01"
    }),
    Review(**{
        "id": 2,
        "movieId": "5678",
        "authorId": -1,
        "rating": 5.5,
        "reviewTitle": "another good movie",
        "reviewBody": "loved the movie too",
        "flagged": False,
        "votes": 0,
        "date": "2022-01-01"
    })]
    mocker.patch("app.services.admin_review_service.list_reviews", return_value=flagged_review)
    result = get_flagged_reviews()
    assert len(result) == 1
    assert all([review.flagged for review in result])

def test_hide_review_hides_review(mocker):
    mocker.patch("app.services.admin_review_service.load_all", return_value=[
    {
        "id": 1,
        "movieId": "1234",
        "authorId": -1,
        "rating": 5.0,
        "reviewTitle": "good movie",
        "reviewBody": "I absolutely loved this movie! The cinematography was stunning and the plot kept me engaged throughout.",
        "flagged": False,
        "votes": 5,
        "date": "2022-01-01",
        "visible": True
    }])
    mocker.patch("app.services.admin_review_service.save_all")
    result = hide_review(1)
    assert not result["visible"]