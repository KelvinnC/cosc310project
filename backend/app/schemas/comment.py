from pydantic import BaseModel
from datetime import date

class Comment(BaseModel):
    id: int
    reviewId: int
    authorId: str
    commentBody: str
    date: date

class CommentCreate(BaseModel):
    reviewId: int
    commentBody: str