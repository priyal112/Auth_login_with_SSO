from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.dependencies.current_user import get_current_user
from app.schemas.AuthSchema import (
    RefreshTokenRequest,
    TokenResponse,
)
from app.schemas.EmailVerificationSchema import (
    EmailVerificationRequest,
    ResendVerificationRequest,
)
from app.schemas.UserSchema import (
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.AuthService import AuthService
from app.services.AuthSessionService import AuthSessionService
from app.services.EmailVerificationService import (
    EmailVerificationService,
)

# router
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
    # Send signup data to the authentication service
    user = await AuthService.signup(
        db,
        data,
    )

    return user


# Email verification API
@router.post(
    "/verify-email",
    response_model=UserResponse,
)
async def verify_email(
    data: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db_session),
):
    # Verify the token and update the user's email status
    user = await EmailVerificationService.verify_email(
        db,
        data.token,
    )

    return user


# Resend the email verification message
@router.post(
    "/resend-verification",
)
async def resend_verification_email(
    data: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db_session),
):
    # Generate a new token and send the verification email
    await EmailVerificationService.resend_verification_email(
        db,
        data.email,
    )
    
    return {
        "message": "If the account exists and is not verified, "
        "a verification email has been sent."
    }


@router.post(
    "/signin",
    response_model=TokenResponse,
)
async def signin(
    data: UserLogin,
    db: AsyncSession = Depends(get_db_session),
):
    # Validate credentials and create JWT
    token = await AuthService.signin(
        db,
        data,
    )

    return token

@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_my_profile(
    current_user = Depends(get_current_user),
):
    # Return the currently authenticated user
    return current_user


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh_access_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db_session),
):
    # Validate the refresh token and create a new access token
    access_token = (
        await AuthSessionService.refresh_access_token(
            db,
            data.refresh_token,
        )
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=data.refresh_token,
        token_type="bearer",
    )

@router.post("/logout")
async def logout(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db_session),
):
    # Revoke the refresh session
    await AuthSessionService.revoke_session(
        db,
        data.refresh_token,
    )

    # Return a simple success message
    return {
        "message": "Successfully logged out."
    }