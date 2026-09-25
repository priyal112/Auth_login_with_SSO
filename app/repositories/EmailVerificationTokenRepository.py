from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.EmailVerificationTokenModel import EmailVerificationToken


class EmailVerificationTokenRepository:

    # Create a new verification token
    @staticmethod
    async def create(
        db: AsyncSession,
        token: EmailVerificationToken,
    ) -> EmailVerificationToken:

        db.add(token)

        await db.commit()

        await db.refresh(token)

        return token

    # Find a verification token using its hash
    @staticmethod
    async def get_by_token_hash(
        db: AsyncSession,
        token_hash: str,
    ) -> EmailVerificationToken | None:

        # Find the token using the stored hash
        result = await db.execute(
            select(EmailVerificationToken).where(
                EmailVerificationToken.token_hash == token_hash
            )
        )

        return result.scalar_one_or_none()

    # Mark a verification token as used
    @staticmethod
    async def mark_as_used(
        db: AsyncSession,
        token: EmailVerificationToken,
    ) -> EmailVerificationToken:

        # Store the current UTC time
        token.used_at = datetime.now(timezone.utc)

        await db.commit()

        await db.refresh(token)

        return token
