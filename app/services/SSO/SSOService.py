from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.UserIdentityModel import UserIdentity
from app.models.UserModel import User
from app.repositories.UserIdentityRepository import UserIdentityRepository
from app.repositories.UserRepository import UserRepository
from app.services.AuthSessionService import AuthSessionService


class SSOService:

    @staticmethod
    async def login(
        db: AsyncSession,
        provider: str,
        provider_user_info: dict,
    ) -> tuple[str, str]:

        # Find or create the application user and identity

        # Get the provider's unique user ID
        provider_user_id = provider_user_info.get(
            "provider_user_id"
        )

        provider_email = provider_user_info.get("email")

        first_name = provider_user_info.get(
            "first_name"
        )

        last_name = provider_user_info.get(
            "last_name"
        )

        if not provider_user_id or not provider_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provider did not return required user information.",
            )

        provider_email = provider_email.lower().strip()

        # STEP 1: Look for an existing provider identity

        identity = await UserIdentityRepository.get_by_provider_user(
            db=db,
            provider=provider,
            provider_user_id=provider_user_id,
        )

        if identity:

            user = await UserRepository.get_by_id(
                db,
                identity.user_id,
            )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Associated user account not found.",
                )

        else:

            # STEP 2: No provider identity exists
            # Check if the user with the same email exists

            user = await UserRepository.get_by_email(
                db,
                provider_email,
            )

            if not user:

                # STEP 3: No user exists
                # Create a new application user

                user = User(
                    first_name=first_name or "",
                    last_name=last_name or "",
                    email=provider_email,

                    password_hash=None,

                    email_verified=provider_user_info.get(
                        "email_verified",
                        False,
                    ),

                    is_active=True,
                )

                user = await UserRepository.create(
                    db,
                    user,
                )

            # STEP 4: Connect the provider identity to our application user

            identity = UserIdentity(
                user_id=user.user_id,
                provider=provider,
                provider_user_id=provider_user_id,
                provider_email=provider_email,
            )

            await UserIdentityRepository.create(
                db,
                identity,
            )

        # STEP 5: Make sure the account is active

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account is inactive.",
            )

        # STEP 6: Create our application's access token

        access_token = create_access_token(
            user.user_id
        )

        # STEP 7: Create our application's refresh session

        refresh_token, _ = await AuthSessionService.create_session(
            db=db,
            user_id=user.user_id,
        )

        return access_token, refresh_token