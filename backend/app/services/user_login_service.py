from app.schemas.user_login import UserLogin
from app.repositories.user_repo import load_all
import bcrypt
from fastapi import HTTPException
import jwt
from datetime import datetime, timedelta, timezone
import os

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT SECRET could not be loaded")

def user_login(payload: UserLogin) -> str:
    users = load_all()
    found_user = next((user for user in users if user.get("username") == payload.username), None)
    if found_user == None:
        raise HTTPException(401, detail="Invalid credentials")
    
    password_valid = bcrypt.checkpw(payload.password.encode("utf-8"), found_user.get("hashed_password").encode("utf-8"))
    if not password_valid:
        raise HTTPException(401, detail="Invalid credentials")
    
    if found_user.get("active") == False:
        raise BannedUserException(403, detail="Account banned")
    
    current_datetime = datetime.now(timezone.utc)
    expiration_time = current_datetime + timedelta(hours=1)
    user_payload = {"user_id": found_user.get("id"),
                    "username": found_user.get("username"),
                    "exp": expiration_time,
                    "role": found_user.get("role")}
    encoded_jwt = jwt.encode(user_payload, JWT_SECRET, algorithm="HS256")
    
    return encoded_jwt
    
class BannedUserException(HTTPException):
    pass