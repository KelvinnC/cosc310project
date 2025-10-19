from pydantic import BaseModel, Field
from typing import List, Annotated, Literal, Optional
from datetime import date
from .review import Review

UsernameStr = Annotated[str, Field(max_length=20, min_length=3)]
PasswordStr = Annotated[str, Field(max_length=20, min_length=8)]

class User(BaseModel):
    """User Schema containing system-level data"""
    id: str
    username: UsernameStr
    hashed_password: str
    role: Literal["user", "admin"]
    created_at: date
    active: bool

class UserCreate(BaseModel):
    """Schema for user registration"""
    username: UsernameStr
    password: PasswordStr

class UserUpdate(BaseModel):
    """Schema for user update"""
    username: Optional[UsernameStr] = None
    password: Optional[PasswordStr] = None