from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.core.dependencies import require_role
from backend.app.modules.students.schemas import StudentProfileResponse, StudentUpdateRequest, ResumeUploadResponse
from backend.app.modules.students.service import get_student_profile, update_student_profile, upload_student_resume
from backend.app.models.user import User

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("/profile", response_model=StudentProfileResponse)
async def profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["student", "tpo", "admin"]))
):
    return await get_student_profile(db, current_user)

@router.put("/profile", response_model=StudentProfileResponse)
async def update_profile(
    update_data: StudentUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["student"]))
):
    return await update_student_profile(db, current_user, update_data)

@router.post("/resume/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["student"]))
):
    return await upload_student_resume(db, current_user, file)
