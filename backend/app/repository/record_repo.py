from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from . import MedicalRecord
import uuid


class RecordRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_record(self, record_model: MedicalRecord) -> MedicalRecord:
        self.db.add(record_model)

        await self.db.flush()
        await self.db.refresh(record_model)
        return record_model
    
    async def get_by_id(self, record_id: uuid.UUID) -> MedicalRecord | None:
        stmt = select(MedicalRecord).where(MedicalRecord.id == record_id)
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()
    
    async def get_all_by_patient(self, dr_id: uuid.UUID, patient_id: uuid.UUID) -> list[MedicalRecord]:
        stmt = select(MedicalRecord).where(
            and_(
                MedicalRecord.doctor_id == dr_id,
                MedicalRecord.patient_id == patient_id
            )
        ).order_by(
            MedicalRecord.uploaded_at.desc()
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def delete_record(self, record_model: MedicalRecord) -> None:
        await self.db.delete(record_model)