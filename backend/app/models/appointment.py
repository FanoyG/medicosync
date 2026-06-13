import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import User, Patient


class Appointment(Base):
    __tablename__ = "appointments"

    id              : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id       : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    patient_id      : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    scheduled_at    : Mapped[datetime]  = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes: Mapped[int]       = mapped_column(Integer, nullable=False, default=30)
    status          : Mapped[str]       = mapped_column(String(20), nullable=False, default="pending")  # pending / confirmed / completed / cancelled / no_show
    created_at      : Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    doctor  : Mapped["User"]    = relationship("User")
    patient : Mapped["Patient"] = relationship("Patient")