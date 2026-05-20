# import pytest
# from httpx import AsyncClient, ASGITransport
# from sqlalchemy import event
# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# from sqlalchemy.pool import StaticPool
# import main
# from app.core.database import Base, get_db

# TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# test_engine = create_async_engine(
#     TEST_DATABASE_URL,
#     connect_args={"check_same_thread": False},
#     poolclass=StaticPool
# )

# # 🛡️ SQLite Foreign Key Enforcer
# @event.listens_for(test_engine.sync_engine, "connect")
# def set_sqlite_pragma(dbapi_connection, connection_record):
#     cursor = dbapi_connection.cursor()
#     cursor.execute("PRAGMA foreign_keys=ON")
#     cursor.close()

# TestingSessionLocal = async_sessionmaker(
#     bind=test_engine, 
#     class_=AsyncSession, 
#     expire_on_commit=False
# )

# @pytest.fixture(scope="session")
# def anyio_backend():
#     return "asyncio"

# @pytest.fixture(autouse=True)
# async def setup_database():
#     async with test_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield
#     async with test_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)

# @pytest.fixture
# async def db_session():
#     async with TestingSessionLocal() as session:
#         yield session

# @pytest.fixture
# async def client(db_session):
#     async def _override_get_db():
#         yield db_session
    
#     main.app.dependency_overrides[get_db] = _override_get_db
    
#     async with AsyncClient(transport=ASGITransport(app=main.app), base_url="http://test") as ac:
#         yield ac
        
#     main.app.dependency_overrides.clear()
