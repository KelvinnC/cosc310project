from app.schemas.user_login import UserLogin
from app.repositories.user_repo import load_all
import bcrypt
from fastapi import HTTPException

def user_login(payload: UserLogin) -> str:
    users = load_all()
    found_user = next((user for user in users if user.get("username") == payload.username), None)
    if found_user == None:
        raise HTTPException(401, detail="Invalid credentials")
    password_valid = bcrypt.checkpw(payload.password.encode("utf-8"), found_user.get("hashed_password").encode("utf-8"))
    if not password_valid:
        raise HTTPException(401, detail="Invalid credentials")
    return "valid login"