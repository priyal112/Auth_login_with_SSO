from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.schemas.UserSchema import UserCreate, UserResponse
from app.services.AuthService import AuthService


# Create the authentication router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# Normal signup API
@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    data: UserCreate,
    db: AsyncSession = Depends(get_db_session),
):
    # Send the signup data to the service layer
    user = await AuthService.signup(
        db,
        data,
    )

    return user