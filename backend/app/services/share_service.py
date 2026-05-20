import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.exception import BadRequestException, NotFoundException
from app.core.security import generate_otp, hash_otp, verify_otp
from app.core.storage import generate_presigned_url
from app.models.share import ShareLink
from app.repository.share_repo import ShareLinkRepository
from app.repository.record_repo import RecordRepository
from app.schemas.schemas import ShareLinkOut, ShareVerifyOut, RecordType


class ShareService:
    def __init__(self, db: Any):
        self.db = db
        self.repo = ShareLinkRepository(self.db)
        self.record_repo = RecordRepository(self.db)

    async def create_share_link(
        self, 
        record_id: uuid.UUID, 
        doctor_id: uuid.UUID, 
        expires_in_hours: int
    ) -> ShareLinkOut:
        """Step 1 to 6: Checks ownership bounds, hashes, and registers container metadata."""
        # Step 1: Verify record exists and belongs to this doctor
        record = await self.record_repo.get_by_id(record_id)
        if not record or record.doctor_id != doctor_id:
            raise NotFoundException(detail="Medical record not found or access denied.")

        # Step 2: Ensure expiration calculation date is in the future
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)

        # Step 3: Generate a random secure token and a 6-digit plain OTP
        secure_token = uuid.uuid4().hex
        plain_otp = generate_otp()

        # Step 4: Hash the OTP using HMAC-SHA256 with the server secret key
        hashed_otp = hash_otp(plain_otp)

        # Step 5: Save token, hashed OTP, expiration, and record metadata to the DB
        share_model = ShareLink(
            record_id=record_id,
            doctor_id=doctor_id,
            token=secure_token,
            verification_code=hashed_otp,
            attempts=0,
            is_active=True,
            expires_at=expires_at
        )
        async with self.db.begin_nested():
            db_link = await self.repo.create_share_link(share_model)

        # Step 6: Return the link token and plain OTP back to the doctor matching your schema
        return ShareLinkOut(
            token=db_link.token,
            expires_at=db_link.expires_at,
            plain_otp_code=plain_otp
        )

    async def verify_share_link(self, token: str, plain_otp: str) -> ShareVerifyOut:
        """Step 1 to 7: Evaluates token states, counts attempts, and converts to ShareVerifyOut data."""
        # Step 1: Fetch link by token
        link = await self.repo.get_by_token(token)
        if not link:
            raise NotFoundException(detail="Share link not found.")

        # Step 2: Check if link is active
        if not link.is_active:
            raise BadRequestException(detail="This share link is no longer active.")

        # Step 3: Check if link has expired
        if link.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            await self.repo.deactivate_link(link.id)
            raise BadRequestException(detail="This share link has expired.")

        # Step 4: Check if wrong attempts are less than 3
        if link.attempts >= 3:
            await self.repo.deactivate_link(link.id)
            raise BadRequestException(detail="Link locked permanently due to excessive wrong attempts.")

        # Step 5: Verify OTP using constant-time comparison
        is_valid = verify_otp(plain_otp, link.verification_code)

        # Step 6: If wrong -> increment attempts counter in the DB and lock if it hits 3
        if not is_valid:
            async with self.db.begin_nested():
                await self.repo.increment_attempts(link.id)
            
            if (link.attempts + 1) >= 3:
                await self.repo.deactivate_link(link.id)
                raise BadRequestException(detail="Invalid code. Link is now locked permanently.")
            
            raise BadRequestException(detail="Invalid verification code provided.")

        # Step 7: If correct -> grant document access and map properties into ShareVerifyOut schema
        record = link.record
        doctor = link.doctor

        download_url = await generate_presigned_url(record.s3_key)
        
        # FIX 1: Safely parse database string value to exact lowercase RecordType Enum variant
        # Uses .value parsing or defaults to your exact 'other' enum option
        db_record_type = getattr(record, "record_type", "other")
        try:
            record_enum = RecordType(db_record_type)
        except ValueError:
            record_enum = RecordType.other

    
        doctor_display_name = getattr(doctor, "full_name", "Medical Practitioner")
        if doctor_display_name.strip().startswith("Dr."):
            final_doctor_string = f"Verified: Record from {doctor_display_name.strip()}"
        else:
            final_doctor_string = f"Verified: Record from Dr. {doctor_display_name.strip()}"


        return ShareVerifyOut(
            record_title=record.title,
            record_type=record_enum,
            download_url=download_url,
            doctor_name=final_doctor_string,
            expires_at=link.expires_at
        )

    async def resend_otp(self, token: str) -> str:
        """Generates a fresh OTP code sequence for active container profiles."""
        link = await self.repo.get_by_token(token)
        if not link or not link.is_active:
            raise NotFoundException(detail="Active share link not found.")

        if link.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            await self.repo.deactivate_link(link.id)
            raise BadRequestException(detail="Cannot refresh codes on an expired share link.")

        new_plain_otp = generate_otp()
        new_hashed_otp = hash_otp(new_plain_otp)

        async with self.db.begin_nested():
            await self.repo.update_otp(link.id, new_hashed_otp)

        return new_plain_otp

    async def revoke_share_link(self, link_id: uuid.UUID, doctor_id: uuid.UUID) -> None:
        """Forcibly alters operational status parameter to inactive state ahead of schedule."""
        link = await self.db.get(ShareLink, link_id)
        if not link:
            raise NotFoundException(detail="Share link footprint not found.")

        if link.doctor_id != doctor_id:
            raise BadRequestException(detail="Unauthorized permission context boundary access request.")

        async with self.db.begin_nested():
            await self.repo.deactivate_link(link_id)
