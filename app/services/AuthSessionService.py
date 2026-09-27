from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
)
from app.models.AuthSessionModel import AuthSession
from app.repositories.AuthSessionRepository import (
    AuthSessionRepository,
)


class AuthSessionService:

    # Refresh token will remain valid for 7 days
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    @staticmethod
    async def create_session(
        db: AsyncSession,
        user_id: int,
    ) -> tuple[str, AuthSession]:

        refresh_token = generate_refresh_token()

        refresh_token_hash = hash_refresh_token(
            refresh_token
        )

        # Calculate refresh session expiration time
        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(
                days=AuthSessionService.REFRESH_TOKEN_EXPIRE_DAYS
            )
        )

        session = AuthSession(
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            expires_at=expires_at,
        )

        session = await AuthSessionRepository.create(
            db,
            session,
        )

        return refresh_token, session

    @staticmethod
    async def refresh_access_token(
        db: AsyncSession,
        refresh_token: str,
    ) -> str:

        # Hash the refresh token received from the client
        refresh_token_hash = hash_refresh_token(
            refresh_token
        )

        # Find the matching session
        session = (
            await AuthSessionRepository
            .get_by_refresh_token_hash(
                db,
                refresh_token_hash,
            )
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token.",
            )

        if session.revoked_at is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh session has been revoked.",
            )

        if session.expires_at <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired.",
            )

        await AuthSessionRepository.update_last_used(
            db,
            session,
        )

        # Create a new short-lived access JWT
        access_token = create_access_token(
            session.user_id
        )

        return access_token

    @staticmethod
    async def revoke_session(
        db: AsyncSession,
        refresh_token: str,
    ) -> None:

        # Hash the refresh token received from the client
        refresh_token_hash = hash_refresh_token(
            refresh_token
        )

        session = (
            await AuthSessionRepository
            .get_by_refresh_token_hash(
                db,
                refresh_token_hash,
            )
        )

        if not session:
            return

        await AuthSessionRepository.revoke(
            db,
            session,
        )