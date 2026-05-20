import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.patient import Patient
from app.models.record import MedicalRecord
from app.models.share import ShareLink


class DashboardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def count_patients(self, doctor_id: uuid.UUID) -> int:
        stmt = select(func.count()).where(Patient.doctor_id == doctor_id)
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def count_records(self, doctor_id: uuid.UUID) -> int:
        stmt = select(func.count()).where(MedicalRecord.doctor_id == doctor_id)
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def count_active_shares(self, doctor_id: uuid.UUID) -> int:
        stmt = select(func.count()).where(
            ShareLink.doctor_id == doctor_id,
            ShareLink.is_active == True
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0