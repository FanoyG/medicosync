import uuid
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exception import BadRequestException, NotFoundException
from app.core.storage import (
    ALLOWED_TYPES,
    generate_s3_key,
    upload_to_s3,
    generate_presigned_url,
    delete_from_s3,
)
from app.models.record import MedicalRecord
from app.repository.record_repo import RecordRepository
from app.repository.patient_repo import PatientRepository
from app.schemas.schemas import RecordOut


class RecordService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RecordRepository(self.db)
        self.patient_repo = PatientRepository(self.db)

    async def upload_record(
        self,
        file: UploadFile,
        patient_id: uuid.UUID,
        doctor_id: uuid.UUID,
        title: str,
        record_type: str,
    ) -> RecordOut:

        # 1. Validate file type
        if file.content_type not in ALLOWED_TYPES:
            raise BadRequestException(
                detail=f"File type '{file.content_type}' not allowed. Use PDF, JPEG, or PNG."
            )

        # 2. Verify patient exists and belongs to this doctor
        patient = await self.patient_repo.get_by_id(patient_id)
        if not patient or patient.doctor_id != doctor_id:
            raise NotFoundException(detail="Patient not found.")

        # 3. Generate unique S3 key
        s3_key = generate_s3_key(doctor_id, file.filename or "upload")

        # 4. Upload file to S3 FIRST — riskiest operation
        await upload_to_s3(
            file_obj=file.file,
            s3_key=s3_key,
            content_type=file.content_type,
        )

        # 5. Save metadata to DB only after S3 confirms success
        async with self.db.begin_nested():
            record_model = MedicalRecord(
                patient_id=patient_id,
                doctor_id=doctor_id,
                title=title,
                record_type=record_type,
                s3_key=s3_key,
                file_type=file.content_type,
            )
            db_record = await self.repo.create_record(record_model)

        # 6. Generate presigned URL for immediate access
        download_url = await generate_presigned_url(db_record.s3_key)

        # 7. Build and return response
        return RecordOut(
            id=db_record.id,
            patient_id=db_record.patient_id,
            doctor_id=db_record.doctor_id,
            title=db_record.title,
            record_type=db_record.record_type,
            download_url=download_url,
            file_type=db_record.file_type,
            uploaded_at=db_record.uploaded_at,
        )

    async def get_record(
        self,
        record_id: uuid.UUID,
        doctor_id: uuid.UUID,
    ) -> RecordOut:

        record = await self.repo.get_by_id(record_id)
        if not record or record.doctor_id != doctor_id:
            raise NotFoundException()

        download_url = await generate_presigned_url(record.s3_key)

        return RecordOut(
            id=record.id,
            patient_id=record.patient_id,
            doctor_id=record.doctor_id,
            title=record.title,
            record_type=record.record_type,
            download_url=download_url,
            file_type=record.file_type,
            uploaded_at=record.uploaded_at,
        )

    async def get_patient_records(
        self,
        patient_id: uuid.UUID,
        doctor_id: uuid.UUID,
    ) -> list[RecordOut]:

        # Verify patient ownership first
        patient = await self.patient_repo.get_by_id(patient_id)
        if not patient or patient.doctor_id != doctor_id:
            raise NotFoundException()

        records = await self.repo.get_all_by_patient(doctor_id, patient_id)

        result = []
        for record in records:
            url = await generate_presigned_url(record.s3_key)
            result.append(RecordOut(
                id=record.id,
                patient_id=record.patient_id,
                doctor_id=record.doctor_id,
                title=record.title,
                record_type=record.record_type,
                download_url=url,
                file_type=record.file_type,
                uploaded_at=record.uploaded_at,
            ))

        return result

    async def delete_record(
        self,
        record_id: uuid.UUID,
        doctor_id: uuid.UUID,
    ) -> None:

        record = await self.repo.get_by_id(record_id)
        if not record or record.doctor_id != doctor_id:
            raise NotFoundException()

        # Delete from S3 first
        await delete_from_s3(record.s3_key)

        # Then delete from DB
        async with self.db.begin_nested():
            await self.repo.delete_record(record)