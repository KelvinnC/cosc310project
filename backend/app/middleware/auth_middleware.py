from fastapi import Request, HTTPException, Depends
from app.services.validate_access import validate_user_access
from app.services.review_service import get_review_by_id

async def jwt_auth_dependency(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code = 401, detail = "Access Token Missing")
    
    access_token = auth_header.split(" ")[1]

    try:
        payload = validate_user_access(access_token)
        return payload
    except Exception as ex:
        raise HTTPException(status_code=401, detail=str(ex))

async def user_is_author(review_id: int, current_user: dict = Depends(jwt_auth_dependency)):
    """Verify that the current user is the author of the review."""
    review = get_review_by_id(review_id)
    user_id = current_user.get("user_id")
    
    if str(review.authorId) != str(user_id):
        raise HTTPException(
            status_code=403,
            detail="You can only modify your own reviews"
        )
    
    return current_user