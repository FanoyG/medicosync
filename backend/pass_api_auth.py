# app/main.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from password_handler import router  # Adjust path to your router import

app = FastAPI(title="MedicoSync Auth Sandbox")

# Include your authentication router
app.include_router(router)

# =====================================================================
# GLOBAL EXCEPTION HANDLERS: This safely protects the Starlette pipe!
# =====================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Catches bad requests or credentials and returns clean JSON without crashing."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )

@app.exception_handler(PermissionError)
async def permission_error_handler(request: Request, exc: PermissionError):
    """Catches rate-limiting lockouts and returns a clean 429 status."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": str(exc)}
    )
