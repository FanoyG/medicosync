from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.schemas import PatientCreate, PatientOut
from ..services.patient_service import PatientService
import uuid

class PatientController:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.service = PatientService(self.db)

    
    async def create_patient_controller(self, body: PatientCreate, doctor_id: uuid.UUID) -> PatientOut:
        create_patient = await self.service.create_patient(body, doctor_id)
        return create_patient
    
    async def get_patient_controller(self, patient_id: uuid.UUID, doctor_id: uuid.UUID) -> PatientOut:
        ext_patient = await self.service.get_patient(patient_id, doctor_id)
        return ext_patient

    async def get_all_patient_controller(self, doctor_id: uuid.UUID) -> list[PatientOut]:
        all_ext_patient = await self.service.get_all_patients(doctor_id)
        return all_ext_patient
    
    async def remove_patient_controller(self, patient_id: uuid.UUID, doctor_id: uuid.UUID):
        result = await self.service.delete_patient(patient_id, doctor_id)
        return None