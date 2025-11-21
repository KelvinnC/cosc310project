from app.services.user_summary_service import get_reviews_by_author, get_user_object, get_user_summary, get_user_by_id, get_users_battles, get_users_reviews

def test_get_users_reviews(mocker):
    mock_get = mocker.patch("app.services.user_summary_service.get_reviews_by_author", return_value=["review1", "review2"])
    result = get_users_reviews(current_user_id=1)
    mock_get.assert_called_once_with(1)
    assert result == ["review1", "review2"]

def test_get_users_battles(mocker):
    mock_get = mocker.patch("app.services.user_summary_service.load_user_battles", return_value=["battle1", "battle2"])
    result = get_users_battles(current_user_id=1)
    mock_get.assert_called_once_with(1)
    assert result == ["battle1", "battle2"]

def test_get_user_object(mocker):
    mock_get = mocker.patch("app.services.user_summary_service.get_user_by_id", return_value="user_obj")
    result = get_user_object(current_user_id=1)
    mock_get.assert_called_once_with(1)
    assert result == "user_obj"

def test_get_user_summary(mocker, user_data):
    from app.schemas.user import User
    from app.schemas.review import Review
    mock_get_reviews = mocker.patch("app.services.user_summary_service.get_reviews_by_author", return_value=[Review(**{
        "id": 1,
        "movieId": "1234",
        "authorId": -1,
        "rating": 5.0,
        "reviewTitle": "good movie",
        "reviewBody": "I absolutely loved this movie! The cinematography was stunning and the plot kept me engaged throughout.",
        "flagged": False,
        "votes": 5,
        "date": "2022-01-01"
    })])
    mock_get_battles = mocker.patch("app.services.user_summary_service.load_user_battles", return_value=["battle1", "battle2"])
    mock_get_user = mocker.patch("app.services.user_summary_service.get_user_by_id", return_value=User(**user_data))

    result = get_user_summary(current_user_id=1)

    mock_get_reviews.assert_called_once_with(1)
    mock_get_battles.assert_called_once_with(1)
    mock_get_user.assert_called_once_with(1)

    assert isinstance(result.user, User)
    assert result.battles == ["battle1", "battle2"]
    assert result.reviews[0].id == 1