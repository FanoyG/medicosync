from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from . import Patient
import uuid

class PatientRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_patient(self, patient_model: Patient) -> Patient:
        self.db.add(patient_model)

        await self.db.flush()
        await self.db.refresh(patient_model)
        return patient_model
    
    async def get_by_id(self, patient_id: uuid.UUID) -> Patient | None:
        stmt = select(Patient).where(Patient.id == patient_id)
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()
    
    async def get_all_by_doctor(self, doctor_id: uuid.UUID) -> list[Patient]:
        stmt = select(Patient).where(Patient.doctor_id == doctor_id)
        result = await self.db.execute(stmt)

        return list(result.scalars().all())
    
    async def delete_patient(self, patient_model: Patient)-> None:
        await self.db.delete(patient_model)

    