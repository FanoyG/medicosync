from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db
from .security import verify_access_token
from ..models import User
from ..repository.user_repo import UserRepository
from uuid import UUID

http_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Verify token & get payload Pydantic object
    payload = verify_access_token(token)
    if payload is None:
        raise credentials_exception

    # 2. Extract UUID string directly (Pydantic guarantees it exists)
    user_id_str = payload.sub

    try:
        uuid_obj = UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    repo = UserRepository(db)
    user = await repo.get_by_id(user_id=uuid_obj)

    # 4. If user does not exist
    if user is None:
        raise credentials_exception

    # 5. Check if account status is active
    if user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN
        )

    # 6. Return user object safely
    return user
