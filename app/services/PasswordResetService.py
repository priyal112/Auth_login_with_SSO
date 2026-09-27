from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    generate_password_reset_token,
    hash_password_reset_token,
)
from app.models.PasswordResetTokenModel import PasswordResetToken
from app.repositories.PasswordResetTokenRepository import (
    PasswordResetTokenRepository,
)
from app.repositories.UserRepository import UserRepository
from app.services.EmailService import EmailService

from app.core.security import (
    generate_password_reset_token,
    hash_password,
    hash_password_reset_token,
)
from fastapi import HTTPException, status

class PasswordResetService:

    RESET_TOKEN_EXPIRE_MINUTES = 30

    @staticmethod
    async def request_password_reset(
        db: AsyncSession,
        email: str,
    ) -> None:

        email = email.lower().strip()

        user = await UserRepository.get_by_email(
            db,
            email,
        )

        if not user:
            return

        raw_token = generate_password_reset_token()

        # Hash the token before storing it
        token_hash = hash_password_reset_token(
            raw_token
        )

        # Calculate token expiration time
        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(
                minutes=PasswordResetService.RESET_TOKEN_EXPIRE_MINUTES
            )
        )

        # Create the password reset token record
        reset_token = PasswordResetToken(
            user_id=user.user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        # Save the token hash in the database
        await PasswordResetTokenRepository.create(
            db,
            reset_token,
        )

        # Send the original token to the user's email
        await EmailService.send_password_reset_email(
            recipient_email=user.email,
            reset_token=raw_token,
        )

    @staticmethod
    async def reset_password(
        db: AsyncSession,
        token: str,
        new_password: str,
    ) -> None:

        token_hash = hash_password_reset_token(token)

        reset_token = await PasswordResetTokenRepository.get_by_token_hash(
            db,
            token_hash,
        )

        # Token does not exist
        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password reset token.",
            )

        # Token has already been used
        if reset_token.used_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password reset token has already been used.",
            )

        # Token has expired
        if reset_token.expires_at <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password reset token has expired.",
            )

        # Find the user associated with this reset token
        user = await UserRepository.get_by_id(
            db,
            reset_token.user_id,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User account not found.",
            )

        user.password_hash = hash_password(new_password)
        reset_token.used_at = datetime.now(timezone.utc)

        await db.commit()