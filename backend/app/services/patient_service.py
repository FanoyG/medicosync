import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exception import NotFoundException
from app.repository.patient_repo import PatientRepository
from app.schemas.schemas import PatientCreate, PatientOut, PatientUpdate
from app.models.patient import Patient


class PatientService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PatientRepository(self.db)

    async def create_patient(
        self, patient_data: PatientCreate, doctor_id: uuid.UUID
    ) -> PatientOut:
        async with self.db.begin_nested():
            patient_dict = patient_data.model_dump(exclude={"full_name"})
            patient_dict["doctor_id"] = doctor_id
            new_patient = await self.repo.create(Patient(**patient_dict))
        return PatientOut.model_validate(new_patient)

    async def get_all_patients(self, doctor_id: uuid.UUID) -> list[PatientOut]:
        patients = await self.repo.get_all_by_doctor(doctor_id)
        return [PatientOut.model_validate(p) for p in patients]

    async def get_patient(
        self, patient_id: uuid.UUID, doctor_id: uuid.UUID
    ) -> PatientOut:
        patient = await self.repo.get_by_id(patient_id, doctor_id)
        if not patient:
            raise NotFoundException(detail="Patient not found.")
        return PatientOut.model_validate(patient)

    async def update_patient(
        self,
        patient_id: uuid.UUID,
        doctor_id: uuid.UUID,
        update_data: PatientUpdate,
    ) -> PatientOut:
        # Strip out all None fields — only patch what was actually sent
        update_fields = update_data.model_dump(exclude_none=True)

        if not update_fields:
            raise NotFoundException(detail="No valid fields provided for update.")

        async with self.db.begin_nested():
            updated = await self.repo.update(patient_id, doctor_id, update_fields)

        if not updated:
            raise NotFoundException(detail="Patient not found.")

        return PatientOut.model_validate(updated)

    async def delete_patient(
        self, patient_id: uuid.UUID, doctor_id: uuid.UUID
    ) -> None:
        async with self.db.begin_nested():
            deleted = await self.repo.delete(patient_id, doctor_id)

        if not deleted:
            raise NotFoundException(detail="Patient not found.")