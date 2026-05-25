from sqlalchemy.ext.asyncio import AsyncSession
from ..core.exception import DuplicateEmailException, UnauthorizedException, NotFoundException
from ..core.security import hash_password, verify_password, create_access_token 
from ..repository.user_repo import UserRepository
from ..schemas.schemas import UserRegister, UserOut, UserLogin, TokenOut
from ..models import User

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(self.db)

    async def register_user(self, user_data: UserRegister) -> UserOut:

        hash_pass = await hash_password(user_data.password)
    
        async with self.db.begin_nested():
            # 1. Look up existing email using 'self.repo' instead of recreating it
            user = await self.repo.exists_by_email(user_data.email)
            if user:
                raise DuplicateEmailException(email=user_data.email)
            

            # 3. Dump the incoming request data excluding plain text password
            user_dict = user_data.model_dump(exclude={"password"})
            user_dict["hashed_password"] = hash_pass

            # 4. Instantiate the SQLAlchemy User model
            db_user_instance = User(**user_dict)

            # 5. Pass the valid User object into the repository write layer using 'self.repo'
            new_user = await self.repo.create_user(db_user_instance)

        # 6. Transform the database instance back into a clean output DTO
        return UserOut.model_validate(new_user)


    async def login_user(self, user_data: UserLogin) -> TokenOut:
        
        user_obj = await self.repo.get_by_email(user_data.email)
        if not user_obj:
            raise UnauthorizedException()
        
        if user_obj.is_active is False:
            raise UnauthorizedException()
        
        is_password_valid = await verify_password(user_data.password, user_obj.hashed_password)
        if not is_password_valid:
            raise UnauthorizedException()
        
        token_payload = {"sub": str(user_obj.id), "role" : "doctor"}
        gen_token = create_access_token(data=token_payload)

        return TokenOut(access_token=gen_token, token_type="bearer", full_name=user_obj.full_name)