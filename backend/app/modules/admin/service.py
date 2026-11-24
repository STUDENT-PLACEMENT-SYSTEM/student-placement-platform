from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from fastapi import HTTPException, status
import uuid
from backend.app.models.recruiter import Recruiter
from backend.app.models.audit_log import AuditLog
from backend.app.models.user import User
from backend.app.modules.admin.schemas import PendingRecruiterResponse, AuditLogResponse
from backend.app.core.redis import publish_event

async def list_pending_recruiters(db: AsyncSession) -> list[PendingRecruiterResponse]:
    result = await db.execute(select(Recruiter).where(Recruiter.is_approved == False))
    rows = result.scalars().all()
    return [
        PendingRecruiterResponse(
            id=r.id,
            company_name=r.company_name,
            contact_person=r.contact_person,
            industry=r.industry,
            website=r.website,
            created_at=r.created_at
        )
        for r in rows
    ]

async def approve_recruiter_account(db: AsyncSession, recruiter_id: uuid.UUID) -> dict:
    result = await db.execute(select(Recruiter).where(Recruiter.id == recruiter_id))
    recruiter = result.scalar_one_or_none()
    if not recruiter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recruiter not found")
    
    recruiter.is_approved = True
    await db.commit()
    return {"message": f"Recruiter {recruiter.company_name} approved successfully"}

async def list_audit_logs(db: AsyncSession, limit: int = 50) -> list[AuditLogResponse]:
    result = await db.execute(select(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit))
    rows = result.scalars().all()
    return [
        AuditLogResponse(
            id=l.id,
            user_id=l.user_id,
            action=l.action,
            entity_name=l.entity_name,
            entity_id=l.entity_id,
            details=l.details,
            created_at=l.created_at
        )
        for l in rows
    ]

async def trigger_ml_retraining() -> dict:
    await publish_event("tasks:ml_retraining", {"trigger": "admin_manual"})
    return {"status": "dispatched", "message": "ML retraining pipeline triggered asynchronously"}
