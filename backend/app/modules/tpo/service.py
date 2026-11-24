from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
import uuid
from datetime import date
from backend.app.models.student import Student, PlacementStatus
from backend.app.models.placement import PlacementOffer, OfferStatus
from backend.app.models.drive import Drive, DriveStatus
from backend.app.models.user import User
from backend.app.modules.tpo.schemas import MarkPlacedRequest, MarkPlacedResponse
from backend.app.core.redis import get_redis_client, publish_event

async def mark_student_as_placed(db: AsyncSession, current_user: User, data: MarkPlacedRequest) -> MarkPlacedResponse:
    stud_res = await db.execute(select(Student).where(Student.id == data.student_id))
    student = stud_res.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    # Create Placement Offer record
    offer = PlacementOffer(
        drive_id=data.drive_id,
        student_id=student.id,
        company_name=data.company_name,
        ctc_lpa=data.ctc_lpa,
        offer_date=date.today(),
        status=OfferStatus.ACCEPTED,
        is_on_campus=data.is_on_campus
    )
    db.add(offer)

    # Update Student placement status
    student.placement_status = PlacementStatus.PLACED
    await db.commit()
    await db.refresh(offer)

    # Invalidate Redis KPI Cache & Publish Real-Time Event for SSE
    try:
        redis = await get_redis_client()
        await redis.delete("kpi:college_summary")
        await publish_event("tpo:live_analytics", {
            "type": "STUDENT_PLACED",
            "student_id": str(student.id),
            "student_name": student.full_name,
            "branch": student.branch,
            "company_name": data.company_name,
            "ctc_lpa": data.ctc_lpa
        })
    except Exception as e:
        print(f"[Warning] Redis event publish error: {e}")

    return MarkPlacedResponse(
        success=True,
        offer_id=offer.id,
        student_id=student.id,
        company_name=data.company_name,
        ctc_lpa=float(data.ctc_lpa),
        message=f"Student {student.full_name} ({student.roll_number}) marked placed at {data.company_name} for {data.ctc_lpa} LPA."
    )

async def approve_drive(db: AsyncSession, current_user: User, drive_id: uuid.UUID, is_approved: bool) -> dict:
    drive_res = await db.execute(select(Drive).where(Drive.id == drive_id))
    drive = drive_res.scalar_one_or_none()
    if not drive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drive not found")

    drive.status = DriveStatus.ACTIVE if is_approved else DriveStatus.CANCELLED
    drive.approved_by_tpo_id = current_user.id
    await db.commit()

    return {"message": f"Drive status updated to {drive.status.value}"}
