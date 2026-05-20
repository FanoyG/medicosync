from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependency import get_current_user
from app.models.user import User
from app.controllers.dashboard_controller import DashboardController
from app.schemas.schemas import DashboardStatsOut

dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def get_dashboard_controller(db: AsyncSession = Depends(get_db)) -> DashboardController:
    return DashboardController(db)

@dashboard_router.get("", response_model=DashboardStatsOut)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    controller: DashboardController = Depends(get_dashboard_controller)
):
    return await controller.get_stats(doctor_id=current_user.id)