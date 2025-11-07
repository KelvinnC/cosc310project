from app.repositories.user_repo import load_all, save_all
from fastapi import HTTPException
from app.services.user_service import get_user_by_id_unsafe
from app.schemas.user import User

def warn_user(user_id: str) -> User:
    user = get_user_by_id_unsafe(user_id)
    if user == None:
        raise HTTPException(404, detail=f"User {user_id} not found")
    user.warnings += 1
    users = [usr for usr in load_all() if usr.get("id") != user_id]
    users.append(user.model_dump(mode="json"))
    save_all(users)
    return user

def unwarn_user(user_id: str) -> User:
    user = get_user_by_id_unsafe(user_id)
    if user == None:
        raise HTTPException(404, detail=f"User {user_id} not found")
    user.warnings = max(0, user.warnings - 1)
    users = [usr for usr in load_all() if usr.get("id") != user_id]
    users.append(user.model_dump(mode="json"))
    save_all(users)
    return user

def ban_user(user_id: str) -> User:
    user = get_user_by_id_unsafe(user_id)
    if user == None:
        raise HTTPException(404, detail=f"User {user_id} not found")
    user.active = False
    users = [usr for usr in load_all() if usr.get("id") != user_id]
    users.append(user.model_dump(mode="json"))
    save_all(users)
    return user

def unban_user(user_id: str) -> User:
    user = get_user_by_id_unsafe(user_id)
    if user == None:
        raise HTTPException(404, detail=f"User {user_id} not found")
    user.active = True
    users = [usr for usr in load_all() if usr.get("id") != user_id]
    users.append(user.model_dump(mode="json"))
    save_all(users)
    return user