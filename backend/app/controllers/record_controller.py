import uuid
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.record_service import RecordService
from app.schemas.schemas import RecordOut


class RecordController:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.service = RecordService(self.db)

    async def upload_record(
        self,
        file: UploadFile,
        patient_id: uuid.UUID,
        doctor_id: uuid.UUID,
        title: str,
        record_type: str,
    ) -> RecordOut:
        return await self.service.upload_record(
            file=file,
            patient_id=patient_id,
            doctor_id=doctor_id,
            title=title,
            record_type=record_type,
        )

    async def get_record(
        self,
        record_id: uuid.UUID,
        doctor_id: uuid.UUID,
    ) -> RecordOut:
        return await self.service.get_record(record_id, doctor_id)

    async def get_patient_records(
        self,
        patient_id: uuid.UUID,
        doctor_id: uuid.UUID,
    ) -> list[RecordOut]:
        return await self.service.get_patient_records(patient_id, doctor_id)

    async def delete_record(
        self,
        record_id: uuid.UUID,
        doctor_id: uuid.UUID,
    ) -> None:
        return await self.service.delete_record(record_id, doctor_id)