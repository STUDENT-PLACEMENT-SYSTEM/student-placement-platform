from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from backend.app.core.database import get_db
from backend.app.core.dependencies import require_role
from backend.app.modules.admin.schemas import PendingRecruiterResponse, AuditLogResponse
from backend.app.modules.admin.service import list_pending_recruiters, approve_recruiter_account, list_audit_logs, trigger_ml_retraining
from backend.app.models.user import User

router = APIRouter(prefix="/admin", tags=["Super Admin"])

@router.get("/recruiters/pending", response_model=list[PendingRecruiterResponse])
async def pending_recruiters(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    return await list_pending_recruiters(db)

@router.patch("/recruiters/{recruiter_id}/approve")
async def approve_recruiter(
    recruiter_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    return await approve_recruiter_account(db, recruiter_id)

@router.get("/audit-logs", response_model=list[AuditLogResponse])
async def audit_logs(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    return await list_audit_logs(db, limit)

@router.post("/ml/retrain")
async def retrain_ml(
    current_user: User = Depends(require_role(["admin"]))
):
    return await trigger_ml_retraining()
