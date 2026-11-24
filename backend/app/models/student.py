import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from backend.app.core.database import Base

class PlacementStatus(str, enum.Enum):
    UNPLACED = "unplaced"
    PLACED = "placed"
    OPTED_OUT = "opted_out"

class Student(Base):
    __tablename__ = "students"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    roll_number = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(150), nullable=False)
    branch = Column(String(100), nullable=False, index=True)
    batch_year = Column(Integer, nullable=False)
    cgpa = Column(Numeric(4, 2), nullable=False, index=True)
    active_backlogs = Column(Integer, default=0, nullable=False)
    history_of_backlogs = Column(Integer, default=0, nullable=False)
    phone = Column(String(20), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    github_url = Column(String(255), nullable=True)
    resume_s3_key = Column(String(500), nullable=True)
    resume_uploaded_at = Column(DateTime(timezone=True), nullable=True)
    parsed_resume = Column(JSONB, nullable=True)
    placement_status = Column(
        Enum(PlacementStatus, name="placement_status_enum", create_type=False, values_callable=lambda obj: [e.value for e in obj]),
        default=PlacementStatus.UNPLACED,
        nullable=False,
        index=True
    )
    is_eligible_for_placements = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="student_profile")
    embeddings = relationship("StudentEmbedding", back_populates="student", cascade="all, delete-orphan")
    applications = relationship("DriveApplication", back_populates="student", cascade="all, delete-orphan")
    offers = relationship("PlacementOffer", back_populates="student", cascade="all, delete-orphan")
    predictions = relationship("MLPrediction", back_populates="student", cascade="all, delete-orphan")
    roadmaps = relationship("SkillGapRoadmap", back_populates="student", cascade="all, delete-orphan")

class StudentEmbedding(Base):
    __tablename__ = "student_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    embedding_type = Column(String(50), nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    metadata_ = Column("metadata", JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    student = relationship("Student", back_populates="embeddings")
