import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.share import ShareLink
from sqlalchemy.orm import selectinload

class ShareLinkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_share_link(self, share_model: ShareLink) -> ShareLink:
        self.db.add(share_model)
        await self.db.flush()
        await self.db.refresh(share_model)
        return share_model

    async def get_by_token(self, token: str) -> ShareLink | None:
        stmt = select(ShareLink).where(ShareLink.token == token).options(
            selectinload(ShareLink.record),
            selectinload(ShareLink.doctor)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def increment_attempts(self, link_id: uuid.UUID) -> bool:
        """
        Increments the access attempts counter for a specific share link.
        Returns True if the link was found and updated, False otherwise.
        """
        # FIX: Use .returning() to safely find out if a row changed
        stmt = (
            update(ShareLink)
            .where(ShareLink.id == link_id)
            .values(attempts=ShareLink.attempts + 1)
            .returning(ShareLink.id)
        )
        result = await self.db.execute(stmt)
        updated_id = result.scalar_one_or_none()
        return updated_id is not None
    
    async def deactivate_link(self, link_id: uuid.UUID) -> bool:
        """
        Deactivates a share link. Returns True if successful, False if not found.
        """
        link = await self.db.get(ShareLink, link_id)
        if link:
            link.is_active = False
            return True
        return False

    async def update_otp(self, link_id: uuid.UUID, new_hashed_otp: str) -> bool:
        """
        Updates the verification code and resets attempts.
        Returns True if the link was found and updated, False otherwise.
        """
        # FIX: Use .returning() instead of checking the rowcount property
        stmt = (
            update(ShareLink)
            .where(ShareLink.id == link_id)
            .values(verification_code=new_hashed_otp, attempts=0)
            .returning(ShareLink.id)
        )
        result = await self.db.execute(stmt)
        updated_id = result.scalar_one_or_none()
        return updated_id is not None
