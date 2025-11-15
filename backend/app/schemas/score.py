from pydantic import BaseModel

class ReviewScore(BaseModel):
    rating: float
    reviewTitle: str
    votes: int = 0


