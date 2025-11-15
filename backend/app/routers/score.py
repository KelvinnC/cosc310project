from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.score import ReviewScore
from app.services.score_service import get_reviews_by_author

router = APIRouter(prefix="/score", tags=["scores"])

@router.get("/{author_id}", response_model=List[ReviewScore])
def get_score(author_id: str):
    try:
        return get_reviews_by_author(author_id)
    except HTTPException as exc:
        if getattr(exc, "status_code", None) == 404:
            return []
        raise