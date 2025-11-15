from fastapi import APIRouter, HTTPException, status, Response, Depends

from app.schemas.battle import Battle, VoteRequest
from app.services import battle_service
from app.services.user_service import get_user_by_id
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
        reviews = review_service.sample_reviews_for_battle(user_id, sample_size=200)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reviews available"
        )
    except (OSError, ValueError) as e:
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
        # Create the battle
        battle = battle_service.createBattle(user, reviews)
        
        response.headers["Location"] = f"/battles/{battle.id}"
        return battle
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Persistence or unexpected errors from service layer
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create battle: {str(e)}"
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


@router.post("/battles/{battle_id}/votes", status_code=204)
def submit_vote(battle_id: str, payload: VoteRequest, current_user: dict = Depends(jwt_auth_dependency)) -> None:
    """
    Submit a vote for a battle.
    
    Returns 204 No Content on success.
    """
    user_id = current_user.get("user_id")
    user = get_user_by_id(user_id)
    
    # Get the battle by ID
    try:
        battle = battle_service.get_battle_by_id(battle_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    # Submit the vote
    try:
        battle_service.submitBattleResult(
            battle=battle,
            winner_id=payload.winnerId,
            user_id=user_id
        )
    except ValueError as e:
        if "already voted" in str(e).lower():
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    
    # Increment the vote count for the winning review
    try:
        review_service.increment_vote(payload.winnerId)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vote recorded but failed to update review count: {str(e)}"
        )
