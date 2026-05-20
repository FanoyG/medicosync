import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, literal

from . import User 

class UserRepository:
    def __init__(self, db: AsyncSession):
        """Inject the DB session ONCE when creating the repository instance."""
        self.db = db

    async def create_user(self, user_model: User) -> User:
        """Accepts a ready SQLAlchemy model, stages it, and fills its ID."""
        self.db.add(user_model)
        
        # Pushes data to PostgreSQL to generate the UUID, but DOES NOT commit yet.
        await self.db.flush()  
        
        # Populates database-generated values (like created_at and id) back into the model
        await self.db.refresh(user_model)  
        
        return user_model

    async def get_by_id(self, user_id: uuid.UUID)-> User | None:
        """Check if user Exit by Checking its id exit in DB."""

        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Check is user exist by checking its eamil exit in DB"""

        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def exists_by_email(self, email: str) -> bool:
        """Asks the database to look for an email and return a raw number 1 if found."""
        query = select(literal(1)).where(User.email == email)
        result = await self.db.execute(query)

        return result.scalar_one_or_none() is not None
    