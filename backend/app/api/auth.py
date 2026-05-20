from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.schemas import UserRegister, UserLogin, UserOut, TokenOut
from ..controllers.auth_controller import AuthController  # Your controller
from ..utils.limiter import limiter

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


# Senior Move: A simple, type-safe factory function that builds your Controller
def get_auth_controller(db: AsyncSession = Depends(get_db)) -> AuthController:
    """Instantiates and returns the AuthController with an open database session context."""
    return AuthController(db)


@auth_router.post(
    "/register", response_model=UserOut, status_code=status.HTTP_201_CREATED
)
@limiter.limit("3/minutes")
async def signup(
    request: Request,
    user_data: UserRegister,
    # Inject the controller instance safely and cleanly here
    controller: AuthController = Depends(get_auth_controller),
):
    """Router boundary for handling new user registrations."""
    return await controller.register_user_controller(body=user_data)


@auth_router.post(
    "/login", response_model=TokenOut, status_code=status.HTTP_200_OK
)
@limiter.limit("3/minutes")
async def signin(
    request: Request,
    user_data: UserLogin,
    controller: AuthController = Depends(get_auth_controller),
):
    """Router boundary for handling secure account authorizations."""
    return await controller.login_user_controller(body=user_data)
