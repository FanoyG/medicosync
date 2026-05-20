import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import User, MedicalRecord


class ShareLink(Base):
    __tablename__ = "share_links"

    id                : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    doctor_id         : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id",          ondelete="CASCADE"), nullable=False)
    record_id         : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("medical_records.id", ondelete="CASCADE"), nullable=False)
    token             : Mapped[str]       = mapped_column(String(255), unique=True, nullable=False, index=True)
    verification_code : Mapped[str]       = mapped_column(String(255), nullable=False)   # stored hashed
    attempts          : Mapped[int]       = mapped_column(Integer, default=0, nullable=False)
    is_active         : Mapped[bool]      = mapped_column(Boolean, default=True, nullable=False)
    expires_at        : Mapped[datetime]  = mapped_column(DateTime(timezone=True), nullable=False)

    # relationships
    doctor : Mapped["User"]          = relationship(back_populates="share_links")
    record : Mapped["MedicalRecord"] = relationship(back_populates="share_links")