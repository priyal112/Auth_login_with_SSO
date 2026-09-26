from app.schemas.AuthSchema import TokenResponse
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.UserModel import User
from app.repositories.UserRepository import UserRepository
from app.schemas.UserSchema import UserCreate, UserLogin
from app.services.EmailService import EmailService
from app.services.EmailVerificationService import (
    EmailVerificationService,
)
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)

from app.schemas.AuthSchema import TokenResponse

class AuthService:

    # Handle normal user signup
    @staticmethod
    async def signup(
        db: AsyncSession,
        data: UserCreate,
    ) -> User:

        email = data.email.lower().strip()

        existing_user = await UserRepository.get_by_email(
            db,
            email,
        )

        if existing_user:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )

        # Hash the user's password
        password_hash = hash_password(data.password)

        # Create the user object
        user = User(
            first_name=data.first_name.strip(),
            last_name=data.last_name.strip(),
            date_of_birth=data.date_of_birth,
            email=email,
            password_hash=password_hash,
            email_verified=False,
            is_active=True,
        )

        # Save the user
        user = await UserRepository.create(
            db,
            user,
        )

        # Generate a verification token
        raw_token = (
            await EmailVerificationService.create_verification_token(
                db,
                user.user_id,
            )
        )

        # Send the original token to the user's email
        await EmailService.send_verification_email(
            recipient_email=user.email,
            verification_token=raw_token,
        )

        # Return the created user
        return user

    @staticmethod
    async def signin(
        db: AsyncSession,
        data: UserLogin,
    ) -> TokenResponse:

        email = data.email.lower().strip()

        user = await UserRepository.get_by_email(
            db,
            email,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        if not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        password_is_valid = verify_password(
            data.password,
            user.password_hash,
        )

        if not password_is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        if not user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email address before signing in.",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account is inactive.",
            )

        # Create a JWT access token for this user
        access_token = create_access_token(
            user.user_id,
        )

        # Return the token to the client
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
        )
