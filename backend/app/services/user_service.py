import uuid
from typing import List, Dict, Any
from fastapi import HTTPException
from app.schemas.user import User, UserCreate, UserUpdate
from app.repositories.user_repo import load_all, save_all
import datetime
import bcrypt

def list_users() -> List[User]:
    """List all registered users"""
    users = [User(**usr) for usr in load_all()]
    for user in users:
        user.hashed_password = None
    return users

def create_user(payload: UserCreate) -> User:
    """Create a new user object and save it to the database"""
    users = load_all()
    new_user_id = str(uuid.uuid4())
    if any(usr.get("id") == new_user_id for usr in users):
        raise HTTPException(status_code=409, detail="ID collision; retry")
    creation_date = datetime.datetime.now()

    #Hash and salt password to prevent plaintext storage of password
    password_in_bytes = payload.password.encode('utf-8')
    salt = bcrypt.gensalt(12)
    hashed_password = bcrypt.hashpw(password_in_bytes, salt)

    new_user = User(id=new_user_id, username=payload.username.strip(), hashed_password=hashed_password.decode('utf-8'), role="user", created_at=creation_date, active=True)
    users.append(new_user.model_dump(mode="json"))
    save_all(users)
    return new_user

def get_user_by_id(user_id: str) -> User:
    """Get a user object by user_id"""
    users = load_all()
    for user in users:
        if str(user.get("id")) == user_id:
            user_instance = User(**user)
            user_instance.hashed_password = None #prevent exposing user passwords
            return user_instance
    raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

def update_user(user_id: str, payload: UserUpdate) -> User:
    """Update a user's username or password by user_id"""
    users = load_all()
    for idx, user in enumerate(users):
        if user.get("id") == user_id:
            username_update = payload.username if payload.username != None else user["username"]
            password_update = user["hashed_password"]
            if (payload.password != None):
                salt = bcrypt.gensalt(12)
                hashed_password = bcrypt.hashpw(payload.password.encode('utf-8'), salt)
                password_update = hashed_password.decode('utf-8')

            updated = User(id=user_id, username=username_update.strip(), hashed_password=password_update, 
                           role=user["role"], created_at=user["created_at"], active=user["active"])
            users[idx] = updated.model_dump(mode="json")
            save_all(users)
            return updated
    raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

def delete_user(user_id: str) -> None:
    """Deletes a user by user_id"""
    users = load_all()
    new_users = [user for user in users if user.get("id") != user_id]
    if len(new_users) == len(users):
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    save_all(new_users)