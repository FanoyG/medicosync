import uuid
from datetime import datetime, date
from sqlalchemy import String, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import User, MedicalRecord

class Patient(Base):
    __tablename__ = "patients"

    id           : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    doctor_id    : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    first_name   : Mapped[str]       = mapped_column(String(100), nullable=False)
    last_name    : Mapped[str]       = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date]      = mapped_column(Date, nullable=False)
    blood_group  : Mapped[str]       = mapped_column(String(10), nullable=True)
    created_at   : Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())
    gender       : Mapped[str] = mapped_column(String(20), nullable=False)

    # relationships
    doctor  : Mapped["User"]              = relationship(back_populates="patients")
    records : Mapped[list["MedicalRecord"]] = relationship(back_populates="patient", cascade="all, delete-orphan")