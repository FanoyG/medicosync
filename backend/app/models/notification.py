import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import User


class Notification(Base):
    __tablename__ = "notifications"

    id           : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id      : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type         : Mapped[str]       = mapped_column(String(50), nullable=False)
    message      : Mapped[str]       = mapped_column(String(255), nullable=False)
    reference_id : Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    is_read      : Mapped[bool]      = mapped_column(Boolean, default=False, nullable=False)
    created_at   : Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    user : Mapped["User"] = relationship("User")