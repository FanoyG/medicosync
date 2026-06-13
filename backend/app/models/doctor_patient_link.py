import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import User, Patient


class DoctorPatientLink(Base):
    __tablename__ = "doctor_patient_links"

    id         : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id  : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    patient_id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    created_at : Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    doctor  : Mapped["User"]    = relationship(back_populates="patient_links")
    patient : Mapped["Patient"] = relationship(back_populates="doctor_links")

    __table_args__ = (
        UniqueConstraint("doctor_id", "patient_id", name="uq_doctor_patient"),
    )