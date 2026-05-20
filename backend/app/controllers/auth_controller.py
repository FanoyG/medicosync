from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.schemas import UserRegister, UserLogin, UserOut, TokenOut
from ..services.auth_service import UserService

class AuthController:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.service = UserService(self.db)

    async def register_user_controller(self, body: UserRegister) -> UserOut:
        # Senior Fix: Let the service internal architecture handle the transaction.
        # This keeps password hashing safely outside of database locks.
        register_user = await self.service.register_user(body)
        return register_user

    async def login_user_controller(self, body: UserLogin) -> TokenOut:
        result = await self.service.login_user(body)
        return result
