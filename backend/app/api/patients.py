from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependency import get_current_user
from app.models.user import User
from app.schemas.schemas import PatientCreate, PatientOut
from app.controllers.patient_controller import PatientController
import uuid

patient_router = APIRouter(prefix="/patients", tags=["Patients"])

def get_patient_controller(db: AsyncSession = Depends(get_db)) -> PatientController:
    return PatientController(db)

@patient_router.post(
    "/", response_model=PatientOut, status_code=status.HTTP_201_CREATED
)
async def create_patient(
    patient_data: PatientCreate,
    current_user: User = Depends(get_current_user),
    controller: PatientController = Depends(get_patient_controller)
):
    return await controller.create_patient_controller(body=patient_data, doctor_id=current_user.id)

@patient_router.get(
    "/", response_model=list[PatientOut], status_code=status.HTTP_200_OK
)
async def get_all_patient(
    current_user: User = Depends(get_current_user),
    controller: PatientController = Depends(get_patient_controller)
):
    return await controller.get_all_patient_controller(doctor_id=current_user.id)

@patient_router.get(
    "/{id}", response_model=PatientOut, status_code=status.HTTP_200_OK
)
async def get_patient_by_id(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    controller: PatientController = Depends(get_patient_controller)
):
    return await controller.get_patient_controller(patient_id=id, doctor_id=current_user.id)

@patient_router.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_patient(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    controller: PatientController = Depends(get_patient_controller)
):
    return await controller.remove_patient_controller(patient_id=id, doctor_id=current_user.id)