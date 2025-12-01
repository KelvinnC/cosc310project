from app.services.comment_service import get_comments_by_review_id, create_comment
from app.schemas.comment import CommentCreate, Comment


def test_get_comments_by_review_id_returns_comments_with_usernames(mocker):
    mocker.patch(
        "app.services.comment_service.load_all",
        return_value=[
            {"id": 1, "reviewId": 10, "authorId": "u1", "commentBody": "Hello", "date": "2024-01-01"}
        ],
    )
    mock_user = mocker.MagicMock()
    mock_user.username = "bob"
    mocker.patch("app.services.comment_service.get_user_by_id", return_value=mock_user)
    result = get_comments_by_review_id(10)
    assert len(result) == 1
    assert result[0]["authorUsername"] == "bob"
    assert result[0]["commentBody"] == "Hello"


def test_get_comments_by_review_id_returns_empty_list_when_no_comments(mocker):
    mocker.patch("app.services.comment_service.load_all", return_value=[])
    result = get_comments_by_review_id(99)
    assert result == []


def test_create_comment_adds_and_saves_comment(mocker):
    mocker.patch(
        "app.services.comment_service.load_all",
        return_value=[{"id": 1, "reviewId": 10, "authorId": "u1", "commentBody": "Old", "date": "2024"}],
    )
    mock_save = mocker.patch("app.services.comment_service.save_all")
    mocker.patch("app.services.comment_service.get_review_by_id", return_value={"id": 10})
    payload = CommentCreate(commentBody="New comment")
    result = create_comment(payload, review_id=10, user_id="user123")
    assert isinstance(result, Comment)
    assert result.id == 2
    assert result.authorId == "user123"
    assert result.commentBody == "New comment"
    saved = mock_save.call_args[0][0]
    assert len(saved) == 2
    assert saved[-1]["commentBody"] == "New comment"


def test_create_comment_starts_at_id_1_if_no_existing_comments(mocker):
    mocker.patch("app.services.comment_service.load_all", return_value=[])
    mocker.patch("app.services.comment_service.save_all")
    mocker.patch("app.services.comment_service.get_review_by_id", return_value={"id": 101})
    payload = CommentCreate(commentBody="First!")
    new = create_comment(payload, review_id=101, user_id="abc")
    assert new.id == 1
    assert new.commentBody == "First!"
