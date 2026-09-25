from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    generate_verification_token,
    hash_verification_token,
)
from app.models.EmailVerificationTokenModel import EmailVerificationToken
from app.repositories.EmailVerificationTokenRepository import (
    EmailVerificationTokenRepository,
)
from app.repositories.UserRepository import UserRepository
from app.services.EmailService import EmailService


class EmailVerificationService:

    # Create a verification token for a user
    @staticmethod
    async def create_verification_token(
        db: AsyncSession,
        user_id: int,
    ) -> str:

        raw_token = generate_verification_token()

        token_hash = hash_verification_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=30
        )

        # Create the database token object
        verification_token = EmailVerificationToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        # Save the token
        await EmailVerificationTokenRepository.create(
            db,
            verification_token,
        )

        # Return the original token
        return raw_token

    # Verify a user's email
    @staticmethod
    async def verify_email(
        db: AsyncSession,
        raw_token: str,
    ):

        # Hash the token received from the user
        token_hash = hash_verification_token(raw_token)

        # Find the token in the database
        verification_token = (
            await EmailVerificationTokenRepository.get_by_token_hash(
                db,
                token_hash,
            )
        )

        # Token does not exist
        if not verification_token:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token.",
            )

        # Check whether the token was already used
        if verification_token.used_at is not None:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token has already been used.",
            )

        # Get the current UTC time
        current_time = datetime.now(timezone.utc)

        # Check whether the token has expired
        if verification_token.expires_at <= current_time:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token has expired.",
            )

        # Find the user associated with this token
        user = await UserRepository.get_by_id(
            db,
            verification_token.user_id,
        )

        # Make sure the user still exists
        if not user:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User account not found.",
            )

        user.email_verified = True

        # Mark the token as used
        await EmailVerificationTokenRepository.mark_as_used(
            db,
            verification_token,
        )

        await db.commit()

        await db.refresh(user)

        return user

    # Create a new verification token and send it by email
    @staticmethod
    async def resend_verification_email(
        db: AsyncSession,
        email: str,
    ) -> None:

        email = email.lower().strip()

        user = await UserRepository.get_by_email(
            db,
            email,
        )

        # Do not reveal whether an email exists in the database
        if not user:
            return

        # If the email is already verified, there is nothing to resend
        if user.email_verified:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified.",
            )

        # Generate a new verification token
        raw_token = await EmailVerificationService.create_verification_token(
            db,
            user.user_id,
        )

        # Send the new token through email
        await EmailService.send_verification_email(
            recipient_email=user.email,
            verification_token=raw_token,
        )