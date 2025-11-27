from pydantic import BaseModel
from datetime import datetime

class Comment(BaseModel):
    id: int
    reviewId: int
    authorId: str
    commentBody: str
    date: datetime

class CommentCreate(BaseModel):
    reviewId: int
    commentBody: str