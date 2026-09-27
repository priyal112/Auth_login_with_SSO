from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.AuthSessionModel import AuthSession


class AuthSessionRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        session: AuthSession,
    ) -> AuthSession:

        db.add(session)

        await db.commit()

        await db.refresh(session)

        return session

    @staticmethod
    async def get_by_refresh_token_hash(
        db: AsyncSession,
        refresh_token_hash: str,
    ) -> AuthSession | None:

        # Find the session using the hashed refresh token
        result = await db.execute(
            select(AuthSession).where(
                AuthSession.refresh_token_hash
                == refresh_token_hash
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def revoke(
        db: AsyncSession,
        session: AuthSession,
    ) -> AuthSession:

        # Mark the session as revoked
        session.revoked_at = datetime.now(timezone.utc)

        await db.commit()

        await db.refresh(session)

        return session

    @staticmethod
    async def update_last_used(
        db: AsyncSession,
        session: AuthSession,
    ) -> AuthSession:

        # Record when this refresh session was last used
        session.last_used_at = datetime.now(timezone.utc)

        await db.commit()

        await db.refresh(session)

        return session