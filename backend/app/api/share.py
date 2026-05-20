import uuid
from typing import Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status, BackgroundTasks, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependency import get_current_user  
from app.controllers.share_controller import ShareController
from app.schemas.schemas import (
    ShareLinkCreate,
    ShareLinkOut,
    ShareVerify,
    ShareVerifyOut
)
from app.utils.limiter import limiter  # Reference to your global Guard instance

share_router = APIRouter(prefix="/shares", tags=["Document Sharing Containers"])

# Reusable cache tracking the 30-second token cool-down timestamp
OTP_COOLDOWN_CACHE: dict[str, datetime] = {}


# 🔥 THE UPGRADE: Controller Dependency Injection Factory Function
def get_share_controller(db: AsyncSession = Depends(get_db)) -> ShareController:
    """Instantiates and returns the controller layer automatically with its DB context."""
    return ShareController(db)


@share_router.post("", response_model=ShareLinkOut, status_code=status.HTTP_201_CREATED)
async def create_share_link(
    payload: ShareLinkCreate,
    current_doctor: Any = Depends(get_current_user),
    controller: ShareController = Depends(get_share_controller)  # Clean injection
):
    """Secure creation interface reserved exclusively for authorized doctors."""
    return await controller.generate_link(payload, doctor_id=current_doctor.id)


@share_router.post("/verify", response_model=ShareVerifyOut, status_code=status.HTTP_200_OK)
async def verify_share_link(
    payload: ShareVerify,
    controller: ShareController = Depends(get_share_controller)  # Clean injection
):
    """Public access validation firewall point for patients verifying access tokens."""
    return await controller.process_verification(payload)


@share_router.post("/resend", status_code=status.HTTP_200_OK)
@limiter.limit("2/minute")  # 🛡️ SlowAPI Abuse Rate-Limit Rule
async def resend_share_otp(
    request: Request,
    token: str,
    background_tasks: BackgroundTasks,
    controller: ShareController = Depends(get_share_controller)  # Clean injection
):
    """Public rotation access point. Enforces anti-spam boundaries before running services."""
    now = datetime.now(timezone.utc)

    # 🛑 30-Second Token Cool-down Check
    if token in OTP_COOLDOWN_CACHE:
        last_requested = OTP_COOLDOWN_CACHE[token]
        time_since_last = (now - last_requested).total_seconds()
        
        if time_since_last < 30:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Please wait {int(30 - time_since_last)} seconds before requesting a new OTP."
            )

    # Directly execute using our cleanly injected controller instance
    response_data = await controller.process_resend(token)
    OTP_COOLDOWN_CACHE[token] = now

    # background_tasks.add_task(send_sms_notification_worker, response_data["plain_otp"])
    return {"message": response_data["message"]}


@share_router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_share_link(
    link_id: uuid.UUID,
    current_doctor: Any = Depends(get_current_user),
    controller: ShareController = Depends(get_share_controller)  # Clean injection
):
    """Instant master revocation command channel used by doctors to lock access windows."""
    await controller.terminate_link(link_id=link_id, doctor_id=current_doctor.id)
