from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
import uuid
from backend.app.models.drive import Drive, DriveApplication, DriveStatus, ApplicationStatus
from backend.app.models.recruiter import Recruiter
from backend.app.models.student import Student
from backend.app.models.user import User, UserRole
from backend.app.modules.drives.schemas import DriveCreateRequest, DriveResponse, ApplicationResponse

async def list_drives(db: AsyncSession, current_user: User) -> list[DriveResponse]:
    query = select(Drive, Recruiter.company_name).join(Recruiter, Drive.recruiter_id == Recruiter.id)
    
    if current_user.role == UserRole.STUDENT:
        query = query.where(Drive.status == DriveStatus.ACTIVE)
    elif current_user.role == UserRole.RECRUITER:
        rec_res = await db.execute(select(Recruiter).where(Recruiter.user_id == current_user.id))
        recruiter = rec_res.scalar_one_or_none()
        if recruiter:
            query = query.where(Drive.recruiter_id == recruiter.id)
            
    result = await db.execute(query)
    rows = result.all()
    
    return [
        DriveResponse(
            id=drive.id,
            recruiter_id=drive.recruiter_id,
            company_name=company_name,
            title=drive.title,
            role_name=drive.role_name,
            job_description=drive.job_description,
            min_cgpa=float(drive.min_cgpa),
            max_backlogs=drive.max_backlogs,
            allowed_branches=drive.allowed_branches,
            ctc_min_lpa=float(drive.ctc_min_lpa),
            ctc_max_lpa=float(drive.ctc_max_lpa),
            job_location=drive.job_location,
            drive_date=drive.drive_date,
            registration_deadline=drive.registration_deadline,
            status=drive.status.value
        )
        for drive, company_name in rows
    ]

async def create_drive(db: AsyncSession, current_user: User, data: DriveCreateRequest) -> DriveResponse:
    rec_res = await db.execute(select(Recruiter).where(Recruiter.user_id == current_user.id))
    recruiter = rec_res.scalar_one_or_none()
    if not recruiter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recruiter profile not found")

    drive = Drive(
        recruiter_id=recruiter.id,
        title=data.title,
        role_name=data.role_name,
        job_description=data.job_description,
        min_cgpa=data.min_cgpa,
        max_backlogs=data.max_backlogs,
        allowed_branches=data.allowed_branches,
        ctc_min_lpa=data.ctc_min_lpa,
        ctc_max_lpa=data.ctc_max_lpa,
        job_location=data.job_location,
        drive_date=data.drive_date,
        registration_deadline=data.registration_deadline,
        status=DriveStatus.PENDING_APPROVAL if not recruiter.is_approved else DriveStatus.ACTIVE
    )
    db.add(drive)
    await db.commit()
    await db.refresh(drive)

    return DriveResponse(
        id=drive.id,
        recruiter_id=drive.recruiter_id,
        company_name=recruiter.company_name,
        title=drive.title,
        role_name=drive.role_name,
        job_description=drive.job_description,
        min_cgpa=float(drive.min_cgpa),
        max_backlogs=drive.max_backlogs,
        allowed_branches=drive.allowed_branches,
        ctc_min_lpa=float(drive.ctc_min_lpa),
        ctc_max_lpa=float(drive.ctc_max_lpa),
        job_location=drive.job_location,
        drive_date=drive.drive_date,
        registration_deadline=drive.registration_deadline,
        status=drive.status.value
    )

async def apply_to_drive(db: AsyncSession, current_user: User, drive_id: uuid.UUID) -> ApplicationResponse:
    stud_res = await db.execute(select(Student).where(Student.user_id == current_user.id))
    student = stud_res.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    drive_res = await db.execute(select(Drive).where(Drive.id == drive_id))
    drive = drive_res.scalar_one_or_none()
    if not drive or drive.status != DriveStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Drive is not open for applications")

    # Eligibility validation
    if float(student.cgpa) < float(drive.min_cgpa):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"CGPA {student.cgpa} is below required {drive.min_cgpa}")
    if student.active_backlogs > drive.max_backlogs:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Active backlogs exceed maximum allowed")
    if drive.allowed_branches and student.branch not in drive.allowed_branches:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Branch {student.branch} is not eligible for this drive")

    # Check already applied
    existing = await db.execute(select(DriveApplication).where(DriveApplication.drive_id == drive.id, DriveApplication.student_id == student.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already applied to this drive")

    app = DriveApplication(
        drive_id=drive.id,
        student_id=student.id,
        status=ApplicationStatus.APPLIED,
        match_score=85.0
    )
    db.add(app)
    await db.commit()
    await db.refresh(app)

    return ApplicationResponse(
        id=app.id,
        drive_id=app.drive_id,
        student_id=app.student_id,
        status=app.status.value,
        match_score=float(app.match_score) if app.match_score else None,
        applied_at=app.applied_at
    )
