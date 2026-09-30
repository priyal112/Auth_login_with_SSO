from fastapi import Request
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import secrets

from app.database.session import get_db_session
from app.dependencies.current_user import get_current_user
from app.schemas.AuthSchema import (
    ForgotPasswordRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
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
from app.services.PasswordResetService import PasswordResetService
from app.services.SSO.GoogleProvider import GoogleProvider
from app.services.SSO.SSOService import SSOService
from app.services.SSO.MicrosoftProvider import MicrosoftProvider

# router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

google_provider = GoogleProvider()

microsoft_provider = MicrosoftProvider()


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


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db_session),
):

    await PasswordResetService.request_password_reset(
        db=db,
        email=data.email,
    )

    return {
        "message": "If an account exists with this email, a password reset link has been sent."
    }


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db_session),
):
    # Reset the user's password after validating the reset token
    await PasswordResetService.reset_password(
        db=db,
        token=data.token,
        new_password=data.password,
    )

    return {
        "message": "Password has been reset successfully."
    }


@router.get("/google/login")
async def google_login():
    # Generate a random state value

    state = secrets.token_urlsafe(32)

    # Create the Google authorization URL
    authorization_url = google_provider.get_authorization_url(
        state=state
    )

    # Redirect the browser to Google
    response = RedirectResponse(
        url=authorization_url
    )

    # Store the state in a browser cookie
    response.set_cookie(
        key="google_oauth_state",
        value=state,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=600,
    )

    return response

@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
):
    # Get the state that we previously stored in the user's browser
    saved_state = request.cookies.get(
        "google_oauth_state"
    )

    # Make sure a state cookie exists
    if not saved_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google OAuth state is missing.",
        )

    # Compare the state returned by Google with the state we originally generated
    if not secrets.compare_digest(
        saved_state,
        state,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Google OAuth state.",
        )

    # Exchange Google's authorization code for Google's OAuth tokens
    token_data = await google_provider.exchange_code(
        code=code
    )

    # Get the user's information from Google
    google_user_info = await google_provider.get_user_info(
        token_data=token_data
    )

    # Find/create the application user and create our own application tokens
    access_token, refresh_token = await SSOService.login(
        db=db,
        provider="google",
        provider_user_info=google_user_info,
    )

    response = {
        "message": "Google login successful.",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

    return response


@router.get("/microsoft/login")
async def microsoft_login():

    state = secrets.token_urlsafe(32)

    authorization_url = microsoft_provider.get_authorization_url(
        state=state
    )

    # Redirect the user's browser to Microsoft
    response = RedirectResponse(
        url=authorization_url
    )

    # Save the state in a secure HTTP-only cookie
    response.set_cookie(
        key="microsoft_oauth_state",
        value=state,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=600,
    )

    return response

@router.get("/microsoft/callback")
async def microsoft_callback(
    code: str,
    state: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
):
    # Get the state value that we saved
    saved_state = request.cookies.get(
        "microsoft_oauth_state"
    )

    # Make sure the state cookie exists
    if not saved_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Microsoft OAuth state is missing.",
        )

    # Compare the state returned by Microsoft with the state we originally generated
    if not secrets.compare_digest(
        saved_state,
        state,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Microsoft OAuth state.",
        )

    # Exchange Microsoft's authorization code for Microsoft's OAuth tokens
    token_data = await microsoft_provider.exchange_code(
        code=code
    )

    # Get the authenticated Microsoft user's information
    microsoft_user_info = await microsoft_provider.get_user_info(
        token_data=token_data
    )

    # Use the common SSO service

    access_token, refresh_token = await SSOService.login(
        db=db,
        provider="microsoft",
        provider_user_info=microsoft_user_info,
    )

    return {
        "message": "Microsoft login successful.",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }