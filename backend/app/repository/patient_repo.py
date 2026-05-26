import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.patient import Patient


class PatientRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, patient: Patient) -> Patient:
        self.db.add(patient)
        await self.db.flush()
        await self.db.refresh(patient)
        return patient

    async def get_all_by_doctor(self, doctor_id: uuid.UUID) -> list[Patient]:
        result = await self.db.execute(
            select(Patient).where(Patient.doctor_id == doctor_id)
        )
        return list(result.scalars().all())

    async def get_by_id(
        self, patient_id: uuid.UUID, doctor_id: uuid.UUID
    ) -> Patient | None:
        result = await self.db.execute(
            select(Patient).where(
                Patient.id == patient_id,
                Patient.doctor_id == doctor_id,
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        patient_id: uuid.UUID,
        doctor_id: uuid.UUID,
        update_fields: dict,
    ) -> Patient | None:
        """Applies only the non-None fields from the patch payload."""
        patient = await self.get_by_id(patient_id, doctor_id)
        if not patient:
            return None

        for field, value in update_fields.items():
            setattr(patient, field, value)

        await self.db.flush()
        await self.db.refresh(patient)
        return patient

    async def delete(
        self, patient_id: uuid.UUID, doctor_id: uuid.UUID
    ) -> bool:
        """Returns True if a row was deleted, False if nothing matched."""
        result = await self.db.execute(
            delete(Patient).where(
                Patient.id == patient_id,
                Patient.doctor_id == doctor_id,
            )
        )
        await self.db.flush()
        # result may be a DBAPI/SQLAlchemy result object; use getattr to avoid
        # static type issues when rowcount isn't known to the type checker.
        return getattr(result, "rowcount", 0) > 0