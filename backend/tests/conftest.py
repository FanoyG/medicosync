import sys
import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.database import Base, get_db
from app.core.config import settings
import slowapi

# 1. WINDOWS EVENT LOOP FIX
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 2. THE SLOWAPI DECORATOR BYPASS (Must live BEFORE importing main)
def dummy_limit_decorator(*args, **kwargs):
    # This acts as a pass-through wrapper that does absolutely nothing
    return lambda func: func
slowapi.Limiter.limit = dummy_limit_decorator

# 3. NOW IT IS SAFE TO IMPORT MAIN
import main

# Use a real PostgreSQL test database
TEST_DATABASE_URL = settings.DB_CONNECTION.replace(
    "medicosync_db", "medicosync_test"
)

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# ─── Create tables before session, drop after ───────────────

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()

# ─── Fresh session per test ──────────────────────────────────

@pytest.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()  # ← clean slate after every test

# ─── Test client ─────────────────────────────────────────────

@pytest.fixture
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    main.app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=main.app),
        base_url="http://test"
    ) as ac:
        yield ac

    main.app.dependency_overrides.clear()

# ==============================================================================
# 🛠️ TEST UTILS & GLOBAL DATA (Your Custom Fixtures Live Here)
# ==============================================================================

@pytest.fixture
async def registered_doctor(client: AsyncClient) -> dict:
    """Creates a doctor and returns their credentials."""
    response = await client.post("/auth/register", json={
        "email": "test@clinic.com",
        "password": "testpass123",
        "full_name": "Dr. Test",
        "specialty": "General"
    })
    assert response.status_code == 201
    return {"email": "test@clinic.com", "password": "testpass123"}

@pytest.fixture
def patient_payload():
    return {
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1990-01-01",
        "gender": "male"
    }

@pytest.fixture
async def auth_token(client: AsyncClient, registered_doctor: dict) -> str:
    """Logs in and returns a Bearer token."""
    response = await client.post("/auth/login", json=registered_doctor)
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
async def auth_headers(auth_token: str) -> dict:
    """Returns Authorization header dict ready to use in tests."""
    return {"Authorization": f"Bearer {auth_token}"}

