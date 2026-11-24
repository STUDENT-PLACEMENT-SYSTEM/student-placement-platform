import uuid
import enum
from datetime import datetime, timezone, date
from sqlalchemy import Column, String, Numeric, Boolean, Date, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class OfferStatus(str, enum.Enum):
    OFFERED = "offered"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class PlacementOffer(Base):
    __tablename__ = "placement_offers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    drive_id = Column(UUID(as_uuid=True), ForeignKey("drives.id", ondelete="SET NULL"), nullable=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    company_name = Column(String(150), nullable=False, index=True)
    ctc_lpa = Column(Numeric(6, 2), nullable=False, index=True)
    offer_letter_s3_key = Column(String(500), nullable=True)
    offer_date = Column(Date, default=date.today, nullable=False)
    status = Column(
        Enum(OfferStatus, name="offer_status_enum", create_type=False, values_callable=lambda obj: [e.value for e in obj]),
        default=OfferStatus.OFFERED,
        nullable=False
    )
    is_on_campus = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    drive = relationship("Drive", back_populates="offers")
    student = relationship("Student", back_populates="offers")
