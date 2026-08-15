import os
import re
import time
import uuid
import jwt
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, field_validator
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app.core.redis_client import redis_client
router = APIRouter()

# =====================================================================
# 1. VALIDATION SCHEMAS (Network Edge Boundary Layer)
# =====================================================================
class PhoneSchema(BaseModel):
    country_code: str = Field(..., description="Example: +91 or +1")
    number: str = Field(..., min_length=10, max_length=10)

    @field_validator("number")
    @classmethod
    def validate_number_digits(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("Phone number must contain only digits")
        return v

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=18)
    full_name: str = Field(min_length=2)
    role: Literal["doctor", "admin", "assistant"]
    gender: Literal["male", "female", "other"]
    phone: PhoneSchema
    specialty: str | None = None

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role_case(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,18}$"
        if not re.match(pattern, v):
            raise ValueError("Password must contain uppercase, lowercase, a number, and a special character.")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_name_characters(cls, v: str) -> str:
        if not re.match(r"^[A-Za-z\s\.\-\']+$", v):
            raise ValueError("Name can only contain letters, spaces, periods, hyphens, or apostrophes.")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str


# =====================================================================
# 2. CORE COMPONENTS (Decoupled Foundation Layers)
# =====================================================================
ph = PasswordHasher()

class PasswordHandler:
    def hash_plain_pwd(self, pln_pwd: str) -> str:
        if not pln_pwd:
            raise ValueError("Plain Password wasn't provided...")
        return ph.hash(pln_pwd)

    def verify_pwd(self, pln_pwd: str, stored_hash: str) -> bool:
        if not pln_pwd or not stored_hash:
            raise ValueError("Required parameters missing for verification.")
        try:
            return ph.verify(stored_hash, pln_pwd)
        except VerifyMismatchError:
            return False

class SessionManager:
    MAX_ATTEMPTS = 5
    LOCKOUT_DURATION = 300

    def __init__(self, redis_client):
        self.redis = redis_client

    async def is_locked_out(self, identifier: str) -> bool:
        if not identifier:
            return False
        return await self.redis.exists(f"lockout:{identifier}") == 1

    async def record_failed_attempt(self, identifier: str) -> None:
        if not identifier:
            raise ValueError("No identifier provided.")
        new_count = await self.redis.incr(f"failed_attempts:{identifier}")
        if new_count >= self.MAX_ATTEMPTS:
            await self.redis.set(f"lockout:{identifier}", "1", ex=self.LOCKOUT_DURATION)

    async def reset_attempts(self, identifier: str) -> None:
        await self.redis.delete(f"failed_attempts:{identifier}", f"lockout:{identifier}")

# class UserRegistration:
#     def __init__(self):
#         self.registered_users = []

#     def is_email_taken(self, email: str) -> bool:
#         for user in self.registered_users:
#             if user["email"] == email:
#                 return True
#         return False 
    
#     def add_user(self, email: str, hashed_password: str, username: str, role: str, gender: str, phone: str) -> None:
#         user_id = str(uuid.uuid4())
#         self.registered_users.append({
#             "user_id": user_id,
#             "email": email,
#             "hashed_password": hashed_password,
#             "username": username,
#             "role": role,
#             "gender": gender,
#             "phone": phone
#         })

#     def get_user_by_email(self, email: str) -> dict | None:
#         for user in self.registered_users:
#             if user["email"] == email:
#                 return user
#         return None


class TokenGenerator:

    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "medicoSync_fallback_secure_key_1111111")
    ALGORITHM = "HS256"

    def __init__(self, redis_client):
        self.redis = redis_client

    def create_access_token(self, user_id: str, role: str) -> str:
        payload = {
            "sub": user_id,
            "role": role,
            "iat": int(time.time()),
            "exp": int(time.time()) + 60
        }
        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def refresh_token(self) -> str:
        return str(uuid.uuid4())

    async def add_refresh_token(self, user_id: str, role: str) -> str:
        token_string = self.refresh_token()
        await self.redis.hset(f"refresh:{token_string}", mapping={"user_id": user_id, "role": role})
        await self.redis.expire(f"refresh:{token_string}", 600)
        return token_string


# =====================================================================
# 3. ORCHESTRATOR LAYER (The Clean Flow Conductor)
# =====================================================================
from auth_repo import UserRepository

class AuthOrchestrator:
    def __init__(self, pwd_handler: PasswordHandler, session_mgr: SessionManager, user_reg: UserRepository, token_gen: TokenGenerator):
        self.pwd_handler = pwd_handler
        self.session_mgr = session_mgr
        self.user_reg = user_reg
        self.token_gen = token_gen

    async def register_user(self, email: str, plain_pwd: str, username: str, role: str, gender: str, country_code: str, phone_number: str) -> dict:
        if await self.user_reg.is_email_taken(email=email):
            raise ValueError("Account already exists with this email.")

        hashed_pwd = self.pwd_handler.hash_plain_pwd(pln_pwd=plain_pwd)
        user = await self.user_reg.add_user(
            email=email, hashed_password=hashed_pwd, username=username,
            role=role, gender=gender, country_code=country_code, phone_number=phone_number,
        )

        access_token = self.token_gen.create_access_token(user_id=str(user.id), role=role)
        refresh_token = await self.token_gen.add_refresh_token(user_id=str(user.id), role=role)
        return {"message": "Registration successful", "access_token": access_token, "refresh_token": refresh_token}

    async def login_user(self, email: str, plain_pwd: str) -> dict:
        if await self.session_mgr.is_locked_out(email):
            raise PermissionError("Too many attempts. Locked out.")

        user = await self.user_reg.get_user_by_email(email=email)
        if not user:
            raise ValueError("Invalid credentials provided.")

        if self.pwd_handler.verify_pwd(pln_pwd=plain_pwd, stored_hash=user.hashed_password):
            await self.session_mgr.reset_attempts(identifier=email)
            access_token = self.token_gen.create_access_token(user_id=str(user.id), role=user.role.value)
            refresh_token = await self.token_gen.add_refresh_token(user_id=str(user.id), role=user.role.value)
            return {"message": "Login successful", "access_token": access_token, "refresh_token": refresh_token}
        else:
            await self.session_mgr.record_failed_attempt(identifier=email)
            raise ValueError("Invalid credentials provided.")

# =====================================================================
# 4. SINGLETON DECLARATION & ENTRYPOINT ROUTING LAYER
# =====================================================================
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db   # use your existing get_db if you already have one
from auth_repo import UserRepository

GLOBAL_PWD_HANDLER = PasswordHandler()
GLOBAL_SESSION_MGR = SessionManager(redis_client=redis_client)
GLOBAL_TOKEN_GEN = TokenGenerator(redis_client=redis_client)

def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_auth_orchestrator(
    repo: UserRepository = Depends(get_user_repository),
) -> AuthOrchestrator:
    return AuthOrchestrator(GLOBAL_PWD_HANDLER, GLOBAL_SESSION_MGR, repo, GLOBAL_TOKEN_GEN)

@router.post("/auth/register")
async def register_endpoint(payload: UserRegister, orchestrator: AuthOrchestrator = Depends(get_auth_orchestrator)):
    result = await orchestrator.register_user(
        email=payload.email, plain_pwd=payload.password, username=payload.full_name,
        role=payload.role, gender=payload.gender,
        country_code=payload.phone.country_code, phone_number=payload.phone.number,
    )
    await orchestrator.user_reg.db.commit()   # temporary — real Controller layer owns this later
    return result

@router.post("/auth/login")
async def login_endpoint(payload: UserLogin, orchestrator: AuthOrchestrator = Depends(get_auth_orchestrator)):
    return await orchestrator.login_user(email=payload.email, plain_pwd=payload.password)

