from fastapi import APIRouter, HTTPException, status, Response, Depends

from app.schemas.battle import Battle, VoteRequest
from app.schemas.review import Review
from app.services import battle_service
from app.services.user_service import get_user_by_id
from app.services import battle_pair_selector
from app.services import review_service
from app.middleware.auth_middleware import jwt_auth_dependency


router = APIRouter(tags=["battles"])

@router.post("/battles", response_model=Battle, status_code=201)
def create_battle(response: Response, current_user: dict = Depends(jwt_auth_dependency)) -> Battle:
    """
    Create a new battle for the authenticated user.
    Returns 201 Created with Location header pointing to the battle resource.
    """
    user_id = current_user.get("user_id")
    user = get_user_by_id(user_id)
    
    try:
        reviews = battle_pair_selector.sample_reviews_for_battle(user_id, sample_size=200)
    except OSError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load reviews: {str(e)}"
        )
    
    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reviews available"
        )
    
    try:
        battle = battle_service.create_battle(user, reviews)
        response.headers["Location"] = f"/battles/{battle.id}"
        return battle
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/battles/{battle_id}", response_model=Battle)
def get_battle(battle_id: str) -> Battle:
    """
    Retrieve a battle by ID.
    
    Returns the battle object with its current state (voted or unvoted).
    """
    try:
        return battle_service.get_battle_by_id(battle_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/battles/{battle_id}/votes", response_model=Review, status_code=200)
def submit_vote(battle_id: str, payload: VoteRequest, current_user: dict = Depends(jwt_auth_dependency)) -> Review:
    """
    Submit a vote for a battle.
    
    Returns the winning review (the one that won this battle) with updated vote count.
    """
    user_id = current_user.get("user_id")
    user = get_user_by_id(user_id)
    
    try:
        battle = battle_service.get_battle_by_id(battle_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    try:
        battle_service.submit_battle_result(
            battle=battle,
            winner_id=payload.winnerId,
            user_id=user_id
        )
    except ValueError as e:
        error_msg = str(e)
        status_code = 409 if "already voted" in error_msg.lower() else 400
        raise HTTPException(status_code=status_code, detail=error_msg)
    
    try:
        review_service.increment_vote(payload.winnerId)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vote recorded but failed to update review count: {str(e)}"
        )
    
    winning_review = review_service.get_review_by_id(payload.winnerId)
    
    return winning_review
