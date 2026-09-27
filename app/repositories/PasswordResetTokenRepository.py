from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.PasswordResetTokenModel import PasswordResetToken


class PasswordResetTokenRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        token: PasswordResetToken,
    ) -> PasswordResetToken:

        db.add(token)
        await db.commit()
        await db.refresh(token)

        return token

    @staticmethod
    async def get_by_token_hash(
        db: AsyncSession,
        token_hash: str,
    ) -> PasswordResetToken | None:

        # Find the reset token using its hash
        result = await db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def mark_as_used(
        db: AsyncSession,
        token: PasswordResetToken,
    ) -> PasswordResetToken:

        token.used_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(token)

        return token