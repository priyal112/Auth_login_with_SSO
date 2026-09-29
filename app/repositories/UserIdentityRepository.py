from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.UserIdentityModel import UserIdentity


class UserIdentityRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        identity: UserIdentity,
    ) -> UserIdentity:

        # Add the new identity record
        db.add(identity)

        await db.commit()

        await db.refresh(identity)

        return identity

    @staticmethod
    async def get_by_provider_user(
        db: AsyncSession,
        provider: str,
        provider_user_id: str,
    ) -> UserIdentity | None:

        # Find an identity using both:
        # provider + provider_user_id

        result = await db.execute(
            select(UserIdentity).where(
                UserIdentity.provider == provider,
                UserIdentity.provider_user_id == provider_user_id,
            )
        )

        return result.scalar_one_or_none()