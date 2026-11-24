from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from backend.app.core.database import get_db
from backend.app.core.dependencies import require_role
from backend.app.modules.tpo.schemas import MarkPlacedRequest, MarkPlacedResponse, DriveApprovalRequest
from backend.app.modules.tpo.service import mark_student_as_placed, approve_drive
from backend.app.models.user import User

router = APIRouter(prefix="/tpo", tags=["Training & Placement Office"])

@router.post("/offers/mark-placed", response_model=MarkPlacedResponse)
async def mark_placed(
    data: MarkPlacedRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["tpo", "admin"]))
):
    return await mark_student_as_placed(db, current_user, data)

@router.patch("/drives/{drive_id}/approve")
async def approve(
    drive_id: uuid.UUID,
    data: DriveApprovalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["tpo", "admin"]))
):
    return await approve_drive(db, current_user, drive_id, data.is_approved)
