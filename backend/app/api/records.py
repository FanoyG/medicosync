import uuid
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependency import get_current_user
from app.models.user import User
from app.schemas.schemas import RecordOut
from app.controllers.record_controller import RecordController

record_router = APIRouter(prefix="/records", tags=["Medical Records"])


def get_record_controller(db: AsyncSession = Depends(get_db)) -> RecordController:
    return RecordController(db)


@record_router.post(
    "/",
    response_model=RecordOut,
    status_code=status.HTTP_201_CREATED
)
async def upload_record(
    patient_id: uuid.UUID = Form(...),
    title: str = Form(...),
    record_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    controller: RecordController = Depends(get_record_controller),
):
    return await controller.upload_record(
        file=file,
        patient_id=patient_id,
        doctor_id=current_user.id,
        title=title,
        record_type=record_type,
    )


@record_router.get(
    "/patient/{patient_id}",
    response_model=list[RecordOut],
    status_code=status.HTTP_200_OK
)
async def get_patient_records(
    patient_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    controller: RecordController = Depends(get_record_controller),
):
    return await controller.get_patient_records(
        patient_id=patient_id,
        doctor_id=current_user.id,
    )


@record_router.get(
    "/{record_id}",
    response_model=RecordOut,
    status_code=status.HTTP_200_OK
)
async def get_record(
    record_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    controller: RecordController = Depends(get_record_controller),
):
    return await controller.get_record(
        record_id=record_id,
        doctor_id=current_user.id,
    )


@record_router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_record(
    record_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    controller: RecordController = Depends(get_record_controller),
):
    return await controller.delete_record(
        record_id=record_id,
        doctor_id=current_user.id,
    )