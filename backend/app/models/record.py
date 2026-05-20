import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Patient, User, ShareLink


class MedicalRecord(Base):
    """
    Represents a medical document (PDF/Image) stored in S3.
    Linked to a Patient (Owner) and a User (Doctor/Uploader).
    """
    __tablename__ = "medical_records"

    id          : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    patient_id  : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id   : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id",    ondelete="CASCADE"), nullable=False, index=True)
    title       : Mapped[str]       = mapped_column(String(255), nullable=False)
    s3_key      : Mapped[str]       = mapped_column(String(500), nullable=False)   # e.g. "uploads/uuid.pdf"
    file_type   : Mapped[str]       = mapped_column(String(100), nullable=False)   # e.g. "application/pdf"
    record_type : Mapped[str] = mapped_column(String(50), nullable=False)
    uploaded_at : Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())


    # relationships
    patient     : Mapped["Patient"]         = relationship("Patient", back_populates="records")
    doctor      : Mapped["User"]            = relationship("User", back_populates="records")
    share_links : Mapped[list["ShareLink"]] = relationship("ShareLink", back_populates="record", cascade="all, delete-orphan")