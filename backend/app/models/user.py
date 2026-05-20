import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Patient, MedicalRecord, ShareLink


class User(Base):
    __tablename__ = "users"

    id              : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email           : Mapped[str]       = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password : Mapped[str]       = mapped_column(String(255), nullable=False)
    full_name       : Mapped[str]       = mapped_column(String(255), nullable=False)
    specialty       : Mapped[str]       = mapped_column(String(100), nullable=True)
    is_active       : Mapped[bool]      = mapped_column(Boolean, default=True, nullable=False)
    created_at      : Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    # relationships
    patients    : Mapped[list["Patient"]]       = relationship(back_populates="doctor", cascade="all, delete-orphan")
    records     : Mapped[list["MedicalRecord"]] = relationship(back_populates="doctor", cascade="all, delete-orphan")
    share_links : Mapped[list["ShareLink"]]     = relationship(back_populates="doctor", cascade="all, delete-orphan")