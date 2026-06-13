import uuid
from datetime import date, datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime, String, ForeignKey, func, UniqueConstraint
from app.core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import User, MedicalRecord

class RecordAccessGrant(Base):
    __tablename__ = "record_access_grants"

    id                   : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    record_id            : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("medical_records.id", ondelete="CASCADE"), nullable=False)
    granted_to_doctor_id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    granted_by_doctor_id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    permission           : Mapped[str]       = mapped_column(String(20), nullable=False, default="read")
    createdd_at          : Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    #relationship
    record               : Mapped["MedicalRecord"] = relationship(back_populates="access_grants")

    __table_args__ = (
        UniqueConstraint("record_id", "granted_to_doctor_id", name="uq_record_grant"),
    )