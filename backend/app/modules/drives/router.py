from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.modules.drives.schemas import DriveCreateRequest, DriveResponse, ApplicationResponse
from backend.app.modules.drives.service import list_drives, create_drive, apply_to_drive
from backend.app.models.user import User

router = APIRouter(prefix="/drives", tags=["Placement Drives"])

@router.get("", response_model=list[DriveResponse])
async def get_drives(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await list_drives(db, current_user)

@router.post("", response_model=DriveResponse, status_code=status.HTTP_201_CREATED)
async def post_drive(
    data: DriveCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["recruiter", "tpo", "admin"]))
):
    return await create_drive(db, current_user, data)

@router.post("/{drive_id}/apply", response_model=ApplicationResponse)
async def apply(
    drive_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["student"]))
):
    return await apply_to_drive(db, current_user, drive_id)
