import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import User


class DoctorConnection(Base):
    __tablename__ = "doctor_connections"

    id            : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requester_id  : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipient_id  : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status        : Mapped[str]       = mapped_column(String(20), nullable=False, default="pending")  # pending / accepted / rejected
    created_at    : Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())
    responded_at  : Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    requester : Mapped["User"] = relationship("User", foreign_keys=[requester_id])
    recipient : Mapped["User"] = relationship("User", foreign_keys=[recipient_id])

    __table_args__ = (
        UniqueConstraint("requester_id", "recipient_id", name="uq_doctor_connection"),
    )