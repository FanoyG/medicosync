from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# Application Module Bindings
from app.core.database import engine
from app.core.exception import AppException
from app.utils.logger import logger
from app.api.auth import auth_router
from app.api.patients import patient_router
from app.api.records import record_router
from app.api.share import share_router
from app.api.dashboard import dashboard_router

from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Engine Tasks
    yield
    # Shutdown Engine Tasks: Safely drop pool resources
    await engine.dispose()

app = FastAPI(
    title="MedicoSync API",
    description="Secure medical portal for doctors",
    version="1.0.0",
    lifespan=lifespan
)

#====================================
# Middleware Configuration Engine
#====================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://medicosync-frontend.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#====================================
# Static File System Mounting
#====================================
# backend_root = Path(__file__).resolve().parent

# # Check if running inside Docker container root path first
# if Path("/frontend").exists():
#     frontend_root = Path("/frontend")
# else:
#     # Fallback pathing rules for local development outside Docker
#     frontend_root = backend_root.parent / "frontend"

# # 1. Mount the core static subfolder (Maps /static/css/... and /static/js/...)
# app.mount("/static", StaticFiles(directory=str(frontend_root / "static")), name="static")

# # 2. Mount the image pool assets directory (Maps /img/...)
# app.mount("/img", StaticFiles(directory=str(frontend_root / "img")), name="img")


#====================================
# Root Static Route (Landing Page)
#====================================
# @app.get("/")
# async def read_index():
#     """Serves the index.html layout automatically at http://127.0.0.1:8000"""
#     frontend_target_path = frontend_root / "index.html"
#     
#     if not frontend_target_path.is_file():
#         logger.error(f"Static route root lookup break. Index asset absent at: {frontend_target_path}")
#         raise HTTPException(status_code=404, detail="Landing page layout file missing.")
#         
#     return FileResponse(str(frontend_target_path))

#====================================
# Dashboard Static Route
#====================================
# @app.get("/dashboard-page")
# async def dashboard():
#     """Serves the dashboard.html layout safely using pathlib objects."""
#     frontend_target_path = frontend_root / "dashboard.html"
#     
#     if not frontend_target_path.is_file():
#         logger.error(f"Static route lookup break. Target asset absent at: {frontend_target_path}")
#         raise HTTPException(status_code=404, detail="Dashboard interface file missing.")
#         
#     return FileResponse(str(frontend_target_path))

#====================================
# Render Production Health Endpoint
#====================================
@app.get("/")
async def production_health():
    """Fallback root point ensuring container health checks pass on Render"""
    return {"status": "healthy", "service": "MedicoSync API Platform"}
 
#====================================
# Include Router Blueprint Bundles
#====================================
app.include_router(auth_router)
app.include_router(patient_router)
app.include_router(record_router)
app.include_router(share_router)
app.include_router(dashboard_router)

#====================================
# Global Exception Handlers
#====================================
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    if exc.status_code >= 400 and exc.status_code < 500:
        client_host = request.client.host if request.client else "Unknown"
        logger.warning(f"Handled Error: {exc.detail} | Path: {request.url.path} | Client: {client_host}")

    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "detail": exc.detail}
    )

@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    logger.error(f"CRITICAL SYSTEM ERROR: {str(exc)} | Path: {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "detail": "Internal Server Error"}
    )

#====================================
# DEBUG TESTING TEMP CODE
#====================================

# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from sqlalchemy.ext.asyncio import AsyncSession
# from fastapi import Depends
# from app.core.database import get_db

# @app.get("/debug-token")
# async def debug_token(
#     credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
#     db: AsyncSession = Depends(get_db)
# ):
#     from app.core.security import verify_access_token
#     from uuid import UUID
#     from app.repository.user_repo import UserRepository

#     payload = verify_access_token(credentials.credentials)
#     if not payload:
#         return {"error": "token invalid"}

#     repo = UserRepository(db)
#     user = await repo.get_by_id(UUID(payload.sub))

#     return {
#         "payload_sub": payload.sub,
#         "user_found": user is not None,
#         "user_active": user.is_active if user else None,
#         "user_id": str(user.id) if user else None
#     }

# @app.get("/debug-raw")
# async def debug_raw(
#     credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
# ):
#     import jwt
#     from app.core.config import settings
    
#     try:
#         raw = jwt.decode(
#             credentials.credentials,
#             settings.SECRET_KEY,
#             algorithms=[settings.ALGORITHM]
#         )
#         return {"decoded": raw, "secret_key": settings.SECRET_KEY[:10] + "..."}
#     except Exception as e:
#         return {"error": str(e)}

# @app.get("/debug-config", include_in_schema=False)
# async def debug_config():
#     from app.core.config import settings
    
#     return {
#         "bucket": settings.S3_BUCKET,
#         "endpoint": settings.AWS_ENDPOINT_URL,
#         "region": settings.AWS_REGION,
#     }
