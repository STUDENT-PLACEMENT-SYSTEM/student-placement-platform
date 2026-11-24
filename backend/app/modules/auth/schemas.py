from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from backend.app.models.user import UserRole

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: UserRole
    full_name: str
    roll_number: Optional[str] = None
    branch: Optional[str] = None
    batch_year: Optional[int] = 2025
    company_name: Optional[str] = None
    industry: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    role: str
    user_id: str

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    role: str
    is_active: bool
    is_verified: bool
