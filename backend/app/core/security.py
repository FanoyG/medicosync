import hmac
import hashlib
import secrets
import jwt
import asyncio

from datetime import datetime, timedelta, timezone
from typing import Any
from argon2 import PasswordHasher
from pydantic import BaseModel, Field, ValidationError
from .config import settings

# ==============================================================================
# 1. CORE SETUP
# ==============================================================================
hasher = PasswordHasher()


class TokenPayload(BaseModel):
    sub: str = Field(..., description="The user identity identifier")
    exp: int = Field(..., description="The token expiration timestamp")
    role: str = Field(..., description="The user access level role (e.g., doctor, patient)")

# ==============================================================================
# 2. PASSWORD COMPONENT (ARGON2 WORKERS)
# ==============================================================================
def _hash_worker(password: str) -> str:
    return hasher.hash(password)


def _verify_worker(hashed_password: str, plain_password: str) -> bool:
    try:
        return hasher.verify(hashed_password, plain_password)
    except Exception:
        return False


async def hash_password(password: str) -> str:
    """Securely hashes a password on a non-blocking background thread worker."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _hash_worker, password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a password on a non-blocking background thread worker."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, _verify_worker, hashed_password, plain_password
    )


# ==============================================================================
# 3. JWT COMPONENT (TOKEN HANDLING)
# ==============================================================================
def create_access_token(data: dict[str, Any]) -> str:
    """Generates a secure, cryptographically signed JSON Web Token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )


def verify_access_token(token: str) -> TokenPayload | None:
    """Decodes, verifies, and strict-validates a token's structure and signature."""
    try:
        payload_dict = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return TokenPayload(**payload_dict)
    except (jwt.PyJWTError, ValidationError):
        return None

# ==============================================================================
# 4. OTP COMPONENT 
# ==============================================================================

def generate_otp() -> str:
    """Generates a cryptographically random 6-digit OTP."""
    return str(secrets.randbelow(1_000_000)).zfill(6)

def hash_otp(otp: str) -> str:
    """Signs the OTP with server secret using HMAC-SHA256."""
    return hmac.new(
        settings.SECRET_KEY.encode(),
        otp.encode(),
        hashlib.sha256
    ).hexdigest()

def verify_otp(plain_otp: str, hashed_otp: str) -> bool:
    """Constant-time comparison with length-leak protection."""
    # 1. Compute the expected hash from what the user typed
    expected = hash_otp(plain_otp)
    expected_bytes = hashlib.sha256(expected.encode()).digest()
    actual_bytes = hashlib.sha256(hashed_otp.encode()).digest()
    
    # FIX 3: Use secrets.compare_digest for modern Python standard
    return secrets.compare_digest(expected_bytes, actual_bytes)
