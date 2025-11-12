from pydantic import BaseModel
from datetime import datetime

class Flag(BaseModel):
    user_id: str
    review_id: int
    timestamp: datetime
