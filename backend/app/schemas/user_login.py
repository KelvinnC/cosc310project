from pydantic import BaseModel, Field
from .user import PasswordStr, UsernameStr

class UserLogin(BaseModel):
    """Schema for UserLogin"""
    username: UsernameStr
    password: PasswordStr