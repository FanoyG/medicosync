import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import TestMedicosyncUser, UserRole, UserGender


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def is_email_taken(self, email: str) -> bool:
        result = await self.db.execute(
            select(TestMedicosyncUser).where(TestMedicosyncUser.email == email)
        )
        return result.scalar_one_or_none() is not None

    async def add_user(
        self, email: str, hashed_password: str, username: str,
        role: str, gender: str, country_code: str, phone_number: str,
    ) -> TestMedicosyncUser:
        new_user = TestMedicosyncUser(
            id=uuid.uuid4(),
            email=email,
            hashed_password=hashed_password,
            full_name=username,
            role=UserRole(role),
            gender=UserGender(gender),
            country_code=country_code,
            phone_number=phone_number,
        )
        self.db.add(new_user)
        await self.db.flush()   # NOT commit — commit happens at router/controller level
        await self.db.refresh(new_user)
        return new_user

    async def get_user_by_email(self, email: str) -> TestMedicosyncUser | None:
        result = await self.db.execute(
            select(TestMedicosyncUser).where(TestMedicosyncUser.email == email)
        )
        return result.scalar_one_or_none()