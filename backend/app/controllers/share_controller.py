import uuid
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.services.share_service import ShareService
from app.schemas.schemas import (
    ShareLinkCreate, 
    ShareLinkOut, 
    ShareVerify, 
    ShareVerifyOut
)

class ShareController:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.service = ShareService(self.db)

    async def generate_link(self, payload: ShareLinkCreate, doctor_id: uuid.UUID) -> ShareLinkOut:
        """Orchestrates link creation and wraps response schemas securely."""
        return await self.service.create_share_link(
            record_id=payload.record_id,
            doctor_id=doctor_id,
            expires_in_hours=payload.expires_in_hours
        )

    async def process_verification(self, payload: ShareVerify) -> ShareVerifyOut:
        """Handles public patient authentication verification pipelines."""
        return await self.service.verify_share_link(
            token=payload.token,
            plain_otp=payload.verification_code
        )

    async def process_resend(self, token: str) -> Dict[str, str]:
        """
        Triggers an OTP rotation sequence. 
        Product Rule: Generates a NEW OTP, and resets wrong attempts tracking to 0.
        """
        new_plain_otp = await self.service.resend_otp(token=token)
        
        # We return the plain code to the router tier so background workers can dispatch it
        return {
            "message": "A new verification code has been generated and dispatched.",
            "plain_otp": new_plain_otp
        }

    async def terminate_link(self, link_id: uuid.UUID, doctor_id: uuid.UUID) -> None:
        """Enforces ownership authorization before revoking an active share container."""
        await self.service.revoke_share_link(link_id=link_id, doctor_id=doctor_id)
