from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=30, pattern="^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    is_verified: bool

    class Config:
        from_attributes = True
