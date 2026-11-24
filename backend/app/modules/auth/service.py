from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from backend.app.models.user import User, UserRole
from backend.app.models.student import Student
from backend.app.models.recruiter import Recruiter
from backend.app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from backend.app.modules.auth.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from backend.app.core.config import settings

async def authenticate_user(db: AsyncSession, creds: LoginRequest) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == creds.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(creds.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": str(user.id), "role": user.role.value})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        role=user.role.value,
        user_id=str(user.id)
    )

async def register_new_user(db: AsyncSession, data: RegisterRequest) -> UserResponse:
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role=data.role,
        is_active=True,
        is_verified=True if data.role == UserRole.STUDENT else False
    )
    db.add(user)
    await db.flush()

    if data.role == UserRole.STUDENT:
        if not data.roll_number or not data.branch:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Roll number and branch are required for students")
        
        student = Student(
            user_id=user.id,
            roll_number=data.roll_number,
            full_name=data.full_name,
            branch=data.branch,
            batch_year=data.batch_year or 2025,
            cgpa=7.00
        )
        db.add(student)
    elif data.role == UserRole.RECRUITER:
        recruiter = Recruiter(
            user_id=user.id,
            company_name=data.company_name or "Independent Recruiter",
            industry=data.industry or "Technology",
            contact_person=data.full_name,
            is_approved=False
        )
        db.add(recruiter)

    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role.value,
        is_active=user.is_active,
        is_verified=user.is_verified
    )
