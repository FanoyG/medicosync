from sqlalchemy.ext.asyncio import AsyncSession
from typing import Type, Any
from app.core.database import Base
from sqlalchemy import select, inspect, desc, asc

class AsyncBaseRepository:
    def __init__(self, db: AsyncSession, model: Any, **kwargs):
        self.db = db
        self.model = model
    

    async def get_by_id(self, id: str):
        """Fetch a single row by ID"""
        
        stmt = select(self.model).where(self.model.id == id)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(self, db_obj: Base) -> Base | None:
        """
        Accepts a fully formed SQLAlchemy model instance,
        saves it, and returns it with generated IDs/timestamps.
        """

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)

        return db_obj

    async def update(self, id: str, **kwargs)-> Base | None:
        """Updates an existing model instance with single or multiple fields dynamically."""

        db_obj = await self.get_by_id(id)

        if not db_obj:
           return None

        for field, value in kwargs.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)

        return db_obj or None
    
    async def get_all(self, skip: int=0, limit: int = 20, sort_by_field: str | None=None, descending: bool = True):
        stmt = select(self.model)

        #checking if the str_filed pass matches the column
        if sort_by_field and hasattr(self.model, sort_by_field):  #<--- sort by given field
            target_sort_column = getattr(self.model, sort_by_field)
        
        elif hasattr(self.model, "created_at"):  # < ---- sort by defult created_at field
            target_sort_column = getattr(self.model, "created_at")
        else:
            target_sort_column = inspect(self.model).primary_key[0]  # < ---- fallback if no defult to primary key column

        # Apply the sorting (defaults to descending for the LIFO box stack)        
        if descending:
            stmt = stmt.order_by(desc(target_sort_column))
        else:
            stmt = stmt.order_by(asc(target_sort_column))
        
        stmt = stmt.offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()


class EmailLookupMixin:
    async def get_by_email(self, email: str):
        """Fetch a single row by email"""

        stmt = select(self.model).where(self.model.email == email) #type: ignore
        result = await self.db.execute(stmt) #type: ignore

        return result.scalar_one_or_none()