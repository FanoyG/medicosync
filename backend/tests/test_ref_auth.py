import uuid
import jwt
import os
import time
import pytest
from argon2.exceptions import VerifyMismatchError
from password_handler import PasswordHandler, SessionManager, TokenGenerator
# Import your class and module-level instance here:
# from your_module import PasswordHandler, PasswordHasher, ph, VerifyMismatchError

import redis.asyncio as redis
import pytest_asyncio

@pytest_asyncio.fixture
async def redis_test_client():
    """Connects to a SEPARATE Redis DB (1) so tests never touch real app data (DB 0)."""
    client = redis.Redis(host="localhost", port=6379, db=1, decode_responses=True)
    await client.flushdb()  # start clean
    yield client
    await client.flushdb()  # clean up after
    await client.aclose()

@pytest.fixture
def handler():
    """Provides a fresh instance of PasswordHandler for each test."""
    return PasswordHandler()


def test_hash_plain_pwd_returns_different_hashes_for_same_password(handler):
    """Verify that hashing the same password twice produces different hash outputs (proves salting)."""
    password = "SecretPassword123!"
    
    hash1 = handler.hash_plain_pwd(password)
    hash2 = handler.hash_plain_pwd(password)
    
    assert hash1 != hash2, "Hashing the same password twice should yield different outputs due to salting."


def test_hash_plain_pwd_returns_different_hashes_for_different_passwords(handler):
    """Verify that hashing two different passwords produces different outputs."""
    hash1 = handler.hash_plain_pwd("FirstPassword123!")
    hash2 = handler.hash_plain_pwd("SecondPassword456!")
    
    assert hash1 != hash2, "Hashing two different passwords should produce different outputs."


def test_verify_pwd_returns_true_for_correct_password(handler):
    """Verify that a correct plain password against its own stored hash returns True."""
    password = "CorrectHorseBatteryStaple"
    stored_hash = handler.hash_plain_pwd(password)
    
    result = handler.verify_pwd(password, stored_hash)
    
    assert result is True, "verify_pwd should return True when the correct plain password is provided."


def test_verify_pwd_returns_false_for_incorrect_password(handler):
    """Verify that an incorrect plain password against a stored hash returns False."""
    correct_password = "MySecurePassword"
    wrong_password = "IncorrectPassword"
    stored_hash = handler.hash_plain_pwd(correct_password)
    
    result = handler.verify_pwd(wrong_password, stored_hash)
    
    assert result is False, "verify_pwd should return False when an incorrect plain password is provided."


def test_hash_plain_pwd_raises_value_error_on_empty_string(handler):
    """Verify that hash_plain_pwd raises ValueError with exact error message when string is empty."""
    with pytest.raises(ValueError) as exc_info:
        handler.hash_plain_pwd("")
        
    assert str(exc_info.value) == "Plain Password wasn't provided...", (
        "Exception message must match 'Plain Password wasn\\'t provided...' exactly."
    )


@pytest.mark.parametrize(
    "pln_pwd, stored_hash",
    [
        ("", "$argon2id$v=19$m=65536,t=3,p=4$somehash..."),
        ("ValidPassword123!", ""),
        ("", ""),
    ],
    ids=["empty_pwd", "empty_hash", "both_empty"]
)
def test_verify_pwd_raises_value_error_on_empty_inputs(handler, pln_pwd, stored_hash):
    """Verify that verify_pwd raises ValueError with exact error message when required parameters are missing."""
    with pytest.raises(ValueError) as exc_info:
        handler.verify_pwd(pln_pwd, stored_hash)
        
    assert str(exc_info.value) == "Required parameters missing for verification.", (
        "Exception message must match 'Required parameters missing for verification.' exactly."
    )


@pytest_asyncio.fixture
async def session_manager(redis_test_client):
    """Provides a fresh instance of SessionManager for each test (async-aware)."""
    return SessionManager(redis_client=redis_test_client)


# ---------------------------------------------------------------------------
# SessionManager tests (asyncified) - use real Redis test client via fixture
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_id", ["", None])
async def test_record_failed_attempt_raises_value_error_on_empty_identifier(session_manager, invalid_id):
    with pytest.raises(ValueError) as exc_info:
        await session_manager.record_failed_attempt(invalid_id)

    assert str(exc_info.value) == "No identifier provided.", "Exception message must match 'No identifier provided.' exactly."


@pytest.mark.asyncio
@pytest.mark.parametrize("unknown_id", ["", None, "unknown_user@example.com"])
async def test_is_locked_out_returns_false_for_unknown_or_empty_identifier(session_manager, unknown_id):
    result = await session_manager.is_locked_out(unknown_id)
    assert result is False, "is_locked_out should return False for unrecorded or empty identifiers."


@pytest.mark.asyncio
async def test_record_failed_attempt_increments_count_without_lockout(session_manager, redis_test_client):
    user = "user_under_limit"
    for i in range(1, 5):
        await session_manager.record_failed_attempt(user)
        val = await redis_test_client.get(f"failed_attempts:{user}")
        assert int(val) == i, f"Expected attempt count to be {i} after attempt #{i}."
        exists = await redis_test_client.exists(f"lockout:{user}")
        assert exists == 0, f"Expected lockout key to not exist on attempt #{i}."
        assert await session_manager.is_locked_out(user) is False


@pytest.mark.asyncio
async def test_record_failed_attempt_locks_out_on_fifth_attempt(session_manager, redis_test_client):
    user = "user_boundary_test"
    # 4 attempts
    for _ in range(4):
        await session_manager.record_failed_attempt(user)

    assert await session_manager.is_locked_out(user) is False

    # 5th attempt should set lockout key
    await session_manager.record_failed_attempt(user)
    cnt = await redis_test_client.get(f"failed_attempts:{user}")
    assert int(cnt) == 5, "Count should be 5 on 5th attempt."
    exists = await redis_test_client.exists(f"lockout:{user}")
    assert exists == 1, "lockout key must exist after reaching MAX_ATTEMPTS"
    ttl = await redis_test_client.ttl(f"lockout:{user}")
    assert 0 < ttl <= session_manager.LOCKOUT_DURATION
    assert await session_manager.is_locked_out(user) is True


@pytest.mark.asyncio
async def test_is_locked_out_returns_false_after_lockout_expires(session_manager, redis_test_client):
    user = "expired_lockout_user"
    for _ in range(5):
        await session_manager.record_failed_attempt(user)

    assert await session_manager.is_locked_out(user) is True

    # Simulate expiry by deleting the lockout key (can't fast-forward Redis time)
    await redis_test_client.delete(f"lockout:{user}")
    assert await session_manager.is_locked_out(user) is False


@pytest.mark.asyncio
async def test_reset_attempts_clears_existing_user_data(session_manager, redis_test_client):
    user = "reset_user"
    for _ in range(5):
        await session_manager.record_failed_attempt(user)

    assert await session_manager.is_locked_out(user) is True

    await session_manager.reset_attempts(user)

    val = await redis_test_client.get(f"failed_attempts:{user}")
    assert val is None, "reset_attempts must remove failed attempts key"
    assert await session_manager.is_locked_out(user) is False


@pytest.mark.asyncio
async def test_reset_attempts_runs_safely_on_non_existent_identifier(session_manager, redis_test_client):
    user = "never_recorded_user"
    # Must run without raising
    await session_manager.reset_attempts(user)
    val = await redis_test_client.get(f"failed_attempts:{user}")
    assert val is None


# Import your class and global DB here:
# from your_module import TokenGenerator, REDIS_SIMULATION_DB, jwt, uuid, time


@pytest.fixture
def generator():
    """Provides a TokenGenerator that does not require Redis (used for sync methods)."""
    return TokenGenerator(redis_client=None)


@pytest_asyncio.fixture
async def async_generator(redis_test_client):
    """Provides a TokenGenerator bound to the async test Redis client."""
    return TokenGenerator(redis_client=redis_test_client)


@pytest_asyncio.fixture(autouse=True)
async def clear_redis_test_db(redis_test_client):
    """Autouse fixture to reset the Redis TEST database (db=1) before and after each test."""
    await redis_test_client.flushdb()
    yield
    await redis_test_client.flushdb()

# ---------------------------------------------------------------------------
# Scenario 1: create_access_token generates valid JWT payload
# ---------------------------------------------------------------------------
def test_create_access_token_generates_valid_jwt_payload(generator, monkeypatch):
    """Scenario 1 (Single-call): Decodes token using SECRET_KEY & HS256 to verify sub, role, iat, exp claims."""
    fixed_time = 1700000000.0
    monkeypatch.setattr(time, "time", lambda: fixed_time)

    user_id = "user_123"
    role = "admin"

    token = generator.create_access_token(user_id=user_id, role=role)

    # Decode using the exact algorithm and key defined in TokenGenerator
    decoded = jwt.decode(token, generator.SECRET_KEY, algorithms=[generator.ALGORITHM], options={"verify_exp": False})

    assert decoded["sub"] == user_id, f"Expected 'sub' claim to be '{user_id}'."
    assert decoded["role"] == role, f"Expected 'role' claim to be '{role}'."
    assert decoded["iat"] == int(fixed_time), f"Expected 'iat' claim to match fixed time integer {int(fixed_time)}."
    assert decoded["exp"] == int(fixed_time) + 60, f"Expected 'exp' claim to match fixed time + 60."


# ---------------------------------------------------------------------------
# Scenario 2: create_access_token expiration duration
# ---------------------------------------------------------------------------
def test_create_access_token_sets_expiration_sixty_seconds_ahead(generator, monkeypatch):
    """Scenario 2 (Single-call): Verifies exp is set exactly 60 seconds ahead of iat timestamp."""
    fixed_time = 1700000500.0
    monkeypatch.setattr(time, "time", lambda: fixed_time)

    token = generator.create_access_token("doc_456", "doctor")
    decoded = jwt.decode(token, generator.SECRET_KEY, algorithms=[generator.ALGORITHM], options={"verify_exp": False})

    expected_iat = int(fixed_time)
    expected_exp = expected_iat + 60

    assert decoded["exp"] - decoded["iat"] == 60, "Token expiration duration must be exactly 60 seconds."
    assert decoded["exp"] == expected_exp, f"Expected 'exp' to equal {expected_exp}."


# ---------------------------------------------------------------------------
# Scenario 4: refresh_token returns a valid UUID4 string format
# ---------------------------------------------------------------------------
def test_refresh_token_returns_valid_uuid4_string(generator):
    """Scenario 4 (Single-call): Verifies output string is a valid parseable UUID4."""
    token = generator.refresh_token()

    assert isinstance(token, str), "refresh_token should return a string."
    
    # Validation check: attempt to instantiate a UUID object from the string
    parsed_uuid = uuid.UUID(token, version=4)
    assert str(parsed_uuid) == token, "refresh_token output must be a valid UUID4 string representation."


# ---------------------------------------------------------------------------
# Scenario 5: refresh_token produces unique values across calls
# ---------------------------------------------------------------------------
def test_refresh_token_generates_unique_values(generator):
    """Scenario 5 (Sequential): Sequential calls to refresh_token produce unique outputs."""
    token1 = generator.refresh_token()
    token2 = generator.refresh_token()

    assert token1 != token2, "Sequential refresh_token calls must generate distinct token strings."


# ---------------------------------------------------------------------------
# Scenario 6: add_refresh_token stores correct metadata in REDIS_SIMULATION_DB
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_add_refresh_token_populates_redis_db(async_generator, monkeypatch, redis_test_client):
    """Scenario 6 (Sequential): Returns token and writes correct payload & TTL to Redis."""
    fixed_time = 1700000000.0
    monkeypatch.setattr(time, "time", lambda: fixed_time)

    user_id = "user_789"
    role = "patient"

    token_key = await async_generator.add_refresh_token(user_id=user_id, role=role)

    stored = await redis_test_client.hgetall(f"refresh:{token_key}")
    assert stored.get("user_id") == user_id
    assert stored.get("role") == role

    ttl = await redis_test_client.ttl(f"refresh:{token_key}")
    assert ttl == 600, f"Expected TTL to be 600 seconds, got {ttl}"


# ---------------------------------------------------------------------------
# Scenario 7: add_refresh_token creates isolated entries for multiple tokens
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_add_refresh_token_creates_distinct_db_entries(async_generator, redis_test_client):
    token1 = await async_generator.add_refresh_token("user_1", "doctor")
    token2 = await async_generator.add_refresh_token("user_2", "admin")

    assert token1 != token2
    keys = await redis_test_client.keys("refresh:*")
    assert len(keys) == 2
    d1 = await redis_test_client.hgetall(f"refresh:{token1}")
    d2 = await redis_test_client.hgetall(f"refresh:{token2}")
    assert d1.get("user_id") == "user_1"
    assert d2.get("user_id") == "user_2"

import time
from enum import Enum
from unittest.mock import AsyncMock, MagicMock
import pytest

# Import your classes here:
from password_handler import (
    AuthOrchestrator,
    PasswordHandler,
    SessionManager,
    UserRepository,
    TokenGenerator,
)


# Mock User Role Enum helper
class UserRole(Enum):
    DOCTOR = "doctor"
    PATIENT = "patient"


# Dummy User Object helper
class DummyUser:
    def __init__(self, user_id="user_123", hashed_password="hashed_pwd_123", role=UserRole.DOCTOR):
        self.id = user_id
        self.hashed_password = hashed_password
        self.role = role


@pytest.fixture
def mock_pwd_handler():
    handler = MagicMock(spec=PasswordHandler)
    handler.hash_plain_pwd.return_value = "hashed_secret_123"
    handler.verify_pwd.return_value = True
    return handler

@pytest.fixture
def mock_user_reg():
    reg = MagicMock(spec=UserRepository)
    reg.is_email_taken = AsyncMock(return_value=False)
    reg.add_user = AsyncMock(return_value=DummyUser())
    reg.get_user_by_email = AsyncMock(return_value=DummyUser())
    return reg


@pytest.fixture
def mock_session_mgr():
    mgr = MagicMock(spec=SessionManager)
    # Async methods must return coroutines using AsyncMock
    mgr.is_locked_out = AsyncMock(return_value=False)
    mgr.record_failed_attempt = AsyncMock()
    mgr.reset_attempts = AsyncMock()
    return mgr


@pytest.fixture
def mock_token_gen():
    gen = MagicMock(spec=TokenGenerator)
    # create_access_token is synchronous
    gen.create_access_token = MagicMock(return_value="mocked_access_token_xyz")
    # add_refresh_token is async
    gen.add_refresh_token = AsyncMock(return_value="mocked_refresh_token_abc")
    return gen


@pytest.fixture
def orchestrator(mock_pwd_handler, mock_session_mgr, mock_user_reg, mock_token_gen):
    return AuthOrchestrator(
        pwd_handler=mock_pwd_handler,
        session_mgr=mock_session_mgr,
        user_reg=mock_user_reg,
        token_gen=mock_token_gen,
    )


# ---------------------------------------------------------------------------
# Scenario 1: register_user fails when email is taken
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_register_user_raises_value_error_when_email_taken(orchestrator, mock_user_reg):
    """Scenario 1: register_user raises ValueError with exact message when email already exists."""
    mock_user_reg.is_email_taken.return_value = True

    with pytest.raises(ValueError) as exc_info:
        await orchestrator.register_user(
            email="existing@example.com",
            plain_pwd="Password123!",
            username="john_doe",
            role="doctor",
            gender="male",
            country_code="+1",
            phone_number="1234567890",
        )

    assert str(exc_info.value) == "Account already exists with this email.", (
        "Exception message must match 'Account already exists with this email.' exactly."
    )


# ---------------------------------------------------------------------------
# Scenario 2: register_user succeeds on unique email
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_register_user_succeeds(orchestrator, mock_pwd_handler, mock_user_reg, mock_token_gen):
    """Scenario 2: register_user hashes password, saves user, generates tokens, and returns success dict."""
    result = await orchestrator.register_user(
        email="newuser@example.com",
        plain_pwd="Password123!",
        username="john_doe",
        role="doctor",
        gender="male",
        country_code="+1",
        phone_number="1234567890",
    )

    mock_pwd_handler.hash_plain_pwd.assert_called_once_with(pln_pwd="Password123!")
    mock_user_reg.add_user.assert_called_once_with(
        email="newuser@example.com",
        hashed_password="hashed_secret_123",
        username="john_doe",
        role="doctor",
        gender="male",
        country_code="+1",
        phone_number="1234567890",
    )
    mock_token_gen.create_access_token.assert_called_once_with(user_id="user_123", role="doctor")
    mock_token_gen.add_refresh_token.assert_called_once_with(user_id="user_123", role="doctor")

    assert result == {
        "message": "Registration successful",
        "access_token": "mocked_access_token_xyz",
        "refresh_token": "mocked_refresh_token_abc",
    }, "Return dictionary must match expected structure and tokens."


# ---------------------------------------------------------------------------
# Scenario 3: login_user fails when locked out
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_login_user_raises_permission_error_when_locked_out(orchestrator, mock_session_mgr):
    """Scenario 3: login_user raises PermissionError with exact message when user is locked out."""
    mock_session_mgr.is_locked_out.return_value = True

    with pytest.raises(PermissionError) as exc_info:
        await orchestrator.login_user(email="locked@example.com", plain_pwd="Password123!")

    assert str(exc_info.value) == "Too many attempts. Locked out.", (
        "Exception message must match 'Too many attempts. Locked out.' exactly."
    )


# ---------------------------------------------------------------------------
# Scenario 4: login_user fails when user is not found
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_login_user_raises_value_error_when_user_not_found(orchestrator, mock_user_reg):
    """Scenario 4: login_user raises ValueError with exact message when email is not found in repository."""
    mock_user_reg.get_user_by_email.return_value = None

    with pytest.raises(ValueError) as exc_info:
        await orchestrator.login_user(email="unknown@example.com", plain_pwd="Password123!")

    assert str(exc_info.value) == "Invalid credentials provided.", (
        "Exception message must match 'Invalid credentials provided.' exactly."
    )


# ---------------------------------------------------------------------------
# Scenario 5: login_user succeeds with valid credentials
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_login_user_succeeds(
    orchestrator, mock_pwd_handler, mock_session_mgr, mock_user_reg, mock_token_gen
):
    """Scenario 5: login_user verifies password, resets attempts, generates tokens with user.role.value, returns dict."""
    user = DummyUser(user_id="user_789", role=UserRole.PATIENT)
    mock_user_reg.get_user_by_email.return_value = user
    mock_pwd_handler.verify_pwd.return_value = True

    result = await orchestrator.login_user(email="patient@example.com", plain_pwd="CorrectPassword123!")

    mock_session_mgr.reset_attempts.assert_called_once_with(identifier="patient@example.com")
    mock_token_gen.create_access_token.assert_called_once_with(user_id="user_789", role="patient")
    mock_token_gen.add_refresh_token.assert_called_once_with(user_id="user_789", role="patient")

    assert result == {
        "message": "Login successful",
        "access_token": "mocked_access_token_xyz",
        "refresh_token": "mocked_refresh_token_abc",
    }, "Return dictionary must match expected login success response."


# ---------------------------------------------------------------------------
# Scenario 6: login_user fails on bad password and records attempt
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_login_user_records_failed_attempt_and_raises_error_on_bad_password(
    orchestrator, mock_pwd_handler, mock_session_mgr
):
    """Scenario 6: login_user records failed attempt and raises ValueError on wrong password."""
    mock_pwd_handler.verify_pwd.return_value = False

    with pytest.raises(ValueError) as exc_info:
        await orchestrator.login_user(email="user@example.com", plain_pwd="WrongPassword!")

    mock_session_mgr.record_failed_attempt.assert_called_once_with(identifier="user@example.com")
    assert str(exc_info.value) == "Invalid credentials provided.", (
        "Exception message must match 'Invalid credentials provided.' exactly."
    )


# Note: the SessionManager behavior with real Redis is covered in the SessionManager tests above.
# Integration tests for AuthOrchestrator use mocks for SessionManager in this suite.


# ---------------------------------------------------------------------------
# Scenario 8: register_user succeeds even if SessionManager reports locked out
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_register_user_succeeds_even_when_session_manager_is_locked_out(
    orchestrator, mock_session_mgr
):
    """Scenario 8: Ensures register_user ignores lockout state and does not check SessionManager.is_locked_out."""
    mock_session_mgr.is_locked_out.return_value = True

    result = await orchestrator.register_user(
        email="locked_email_register@example.com",
        plain_pwd="Password123!",
        username="locked_user",
        role="doctor",
        gender="female",
        country_code="+1",
        phone_number="0987654321",
    )

    # Confirm is_locked_out was never called during registration
    mock_session_mgr.is_locked_out.assert_not_called()
    assert result["message"] == "Registration successful", (
        "register_user must succeed regardless of SessionManager lockout state."
    )