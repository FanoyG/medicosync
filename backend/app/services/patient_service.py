import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.schemas import PatientCreate, PatientOut
from ..repository.patient_repo import PatientRepository
from app.models.patient import Patient # Your SQLAlchemy Database Model class
from app.core.exception import NotFoundException, ForbiddenException, BadRequestException

class PatientService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PatientRepository(self.db)

    async def create_patient(self, patient_data: PatientCreate, doctor_id: uuid.UUID) -> PatientOut:
        """Validates input, maps Pydantic schemas to DB models, and registers a patient safely."""
        incoming_full_name = patient_data.full_name.lower()

        async with self.db.begin_nested():
            # 1. Query existing records to evaluate structural duplicates
            existing_patients = await self.repo.get_all_by_doctor(doctor_id)
            for p in existing_patients:
                existing_full_name = f"{p.first_name} {p.last_name}".strip().lower()
                
                if (existing_full_name == incoming_full_name and 
                    p.date_of_birth == patient_data.date_of_birth):
                    raise BadRequestException()
            
            # 2. Extract Pydantic values as a raw dictionary and unpack them straight into a DB model
            patient_dict = patient_data.model_dump(exclude={"full_name"})
            patient_dict["doctor_id"] = doctor_id          
            patient_model = Patient(**patient_dict)
            
            db_patient = await self.repo.create_patient(patient_model)
            
        # 4. Strict Validation: Parse the output database model into a clean Pydantic out-schema block
        return PatientOut.model_validate(db_patient)

    async def get_patient(self, patient_id: uuid.UUID, doctor_id: uuid.UUID) -> PatientOut:
        """Retrieves a single patient profile after executing cross-pool security authorization checks."""
        db_patient = await self.repo.get_by_id(patient_id)
        if not db_patient:
            raise NotFoundException()
            
        # Isolation Security Guard: Restrict cross-tenant or multi-doctor peek breaches
        if db_patient.doctor_id != doctor_id:
            raise NotFoundException()
            
        return PatientOut.model_validate(db_patient)

    async def get_all_patients(self, doctor_id: uuid.UUID) -> list[PatientOut]:
        """Gathers all medical patient files belonging exclusively to the requesting doctor session."""
        db_patients = await self.repo.get_all_by_doctor(doctor_id)
        
        # Performance Loop: Validate every individual row entity seamlessly using a list comprehension
        return [PatientOut.model_validate(p) for p in db_patients]

    async def delete_patient(self, patient_id: uuid.UUID, doctor_id: uuid.UUID):
        """Wipes a patient record entirely from storage systems after establishing valid access tokens."""
        async with self.db.begin_nested():
            db_patient = await self.repo.get_by_id(patient_id)
            if not db_patient or db_patient.doctor_id != doctor_id:
                raise NotFoundException()
                
            await self.repo.delete_patient(db_patient)
            return None