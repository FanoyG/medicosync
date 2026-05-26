import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import PatientCreate, PatientOut, PatientUpdate
from app.services.patient_service import PatientService


class PatientController:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.service = PatientService(self.db)

    async def create_patient_controller(
        self, body: PatientCreate, doctor_id: uuid.UUID
    ) -> PatientOut:
        return await self.service.create_patient(body, doctor_id)

    async def get_all_patient_controller(
        self, doctor_id: uuid.UUID
    ) -> list[PatientOut]:
        return await self.service.get_all_patients(doctor_id)

    async def get_patient_controller(
        self, patient_id: uuid.UUID, doctor_id: uuid.UUID
    ) -> PatientOut:
        return await self.service.get_patient(patient_id, doctor_id)

    async def update_patient_controller(
        self,
        patient_id: uuid.UUID,
        doctor_id: uuid.UUID,
        body: PatientUpdate,
    ) -> PatientOut:
        return await self.service.update_patient(patient_id, doctor_id, body)

    async def remove_patient_controller(
        self, patient_id: uuid.UUID, doctor_id: uuid.UUID
    ) -> None:
        return await self.service.delete_patient(patient_id, doctor_id)