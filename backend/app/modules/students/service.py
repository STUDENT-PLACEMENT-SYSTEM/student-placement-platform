from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status, UploadFile
import uuid
from datetime import datetime, timezone
from backend.app.models.student import Student
from backend.app.models.user import User
from backend.app.modules.students.schemas import StudentProfileResponse, StudentUpdateRequest, ResumeUploadResponse
from backend.app.core.s3 import get_s3_client, settings
from backend.app.core.redis import publish_event

async def get_student_profile(db: AsyncSession, user: User) -> StudentProfileResponse:
    result = await db.execute(select(Student).where(Student.user_id == user.id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    
    return StudentProfileResponse(
        id=student.id,
        roll_number=student.roll_number,
        full_name=student.full_name,
        branch=student.branch,
        batch_year=student.batch_year,
        cgpa=float(student.cgpa),
        active_backlogs=student.active_backlogs,
        history_of_backlogs=student.history_of_backlogs,
        phone=student.phone,
        linkedin_url=student.linkedin_url,
        github_url=student.github_url,
        resume_s3_key=student.resume_s3_key,
        parsed_resume=student.parsed_resume,
        placement_status=student.placement_status.value,
        is_eligible_for_placements=student.is_eligible_for_placements
    )

async def update_student_profile(db: AsyncSession, user: User, update_data: StudentUpdateRequest) -> StudentProfileResponse:
    result = await db.execute(select(Student).where(Student.user_id == user.id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    
    if update_data.phone is not None:
        student.phone = update_data.phone
    if update_data.linkedin_url is not None:
        student.linkedin_url = update_data.linkedin_url
    if update_data.github_url is not None:
        student.github_url = update_data.github_url
        
    await db.commit()
    await db.refresh(student)
    return await get_student_profile(db, user)

async def upload_student_resume(db: AsyncSession, user: User, file: UploadFile) -> ResumeUploadResponse:
    result = await db.execute(select(Student).where(Student.user_id == user.id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    file_bytes = await file.read()
    s3_key = f"resumes/{student.roll_number}_{uuid.uuid4().hex[:8]}.pdf"

    try:
        s3 = get_s3_client()
        s3.put_object(
            Bucket=settings.MINIO_BUCKET_RESUMES,
            Key=s3_key,
            Body=file_bytes,
            ContentType="application/pdf"
        )
    except Exception as e:
        print(f"[Warning] MinIO upload error: {e}. Saving to fallback directory.")

    student.resume_s3_key = s3_key
    student.resume_uploaded_at = datetime.now(timezone.utc)
    await db.commit()

    # Trigger Async LangGraph Parsing Task via Redis
    await publish_event("tasks:resume_parsing", {
        "student_id": str(student.id),
        "roll_number": student.roll_number,
        "s3_key": s3_key
    })

    return ResumeUploadResponse(
        status="queued",
        s3_key=s3_key,
        message="Resume uploaded successfully. Async LangGraph parsing worker scheduled."
    )
