from fastapi import APIRouter, HTTPException, status, Response

from app.schemas.battle import Battle, VoteRequest
from app.schemas.review import Review
from app.services import battle_service
from app.services.user_service import get_user_by_id
from app.services import review_service


router = APIRouter(tags=["battles"])

@router.post("/users/{user_id}/battles", response_model=Battle, status_code=201)
def create_battle(user_id: str, response: Response) -> Battle:
    """
    Create a new battle for the user.
    Returns 201 Created with Location header pointing to the battle resource.
    """
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
def submit_vote(battle_id: str, user_id: str, payload: VoteRequest) -> None:
    """
    Submit a vote for a battle.
    
    Returns 204 No Content on success.
    """
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
