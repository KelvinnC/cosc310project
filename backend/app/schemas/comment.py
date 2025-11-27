from pydantic import BaseModel
from datetime import date

class Comment(BaseModel):
    commentId: int
    reviewId: int
    authorId: str
    commentBody: str
    date: date