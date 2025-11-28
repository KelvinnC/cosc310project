from typing import List, Dict, Any
from fastapi import HTTPException
from app.schemas.comment import Comment, CommentCreate
from app.repositories.comments_repo import load_all, save_all
from app.services.review_service import get_review_by_id
import datetime

def get_comments_by_movie_id(reviewId: int) -> List[Comment]:
    """Get all comments for a certain review"""
    comments_for_id = [Comment(**comment) for comment in load_all() if comment["reviewId"] == reviewId]
    return comments_for_id

def create_comment(payload: CommentCreate, review_id: int, user_id: str) -> Comment:
    review = get_review_by_id(review_id)
    comments = load_all()
    new_comment_id = max((com.get("id", 0) for com in comments), default=0) + 1

    new_comment = Comment(id=new_comment_id, reviewId=review_id, authorId=user_id, commentBody=payload.commentBody, date=datetime.datetime.now())
    comments.append(new_comment.model_dump(mode="json"))
    save_all(comments)
    return new_comment