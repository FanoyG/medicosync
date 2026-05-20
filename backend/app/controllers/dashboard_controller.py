import uuid
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.dashboard_repo import DashboardRepository
from app.schemas.schemas import DashboardStatsOut # Assuming standard schema path

class DashboardController:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DashboardRepository(self.db)

    async def get_stats(self, doctor_id: uuid.UUID) -> DashboardStatsOut:
        """Fetches all metrics concurrently from the database repository layer."""
        patients, records, shares = await asyncio.gather(
            self.repo.count_patients(doctor_id),
            self.repo.count_records(doctor_id),
            self.repo.count_active_shares(doctor_id)
        )
        
        return DashboardStatsOut(
            total_patients=patients,
            total_records=records,
            active_shares=shares
        )
