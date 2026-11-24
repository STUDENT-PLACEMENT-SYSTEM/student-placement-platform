from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user
from backend.app.modules.auth.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from backend.app.modules.auth.service import authenticate_user, register_new_user
from backend.app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await register_new_user(db, data)

@router.post("/login", response_model=TokenResponse)
async def login(creds: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await authenticate_user(db, creds)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified
    )
