from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.UserModel import User
from app.repositories.UserRepository import UserRepository
from app.schemas.UserSchema import UserCreate


class AuthService:

    # Handle normal user signup
    @staticmethod
    async def signup(
        db: AsyncSession,
        data: UserCreate,
    ) -> User:

        email = data.email.lower().strip()

        # Check whether an account already exists
        existing_user = await UserRepository.get_by_email(
            db,
            email,
        )

        if existing_user:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )

        # Convert the plain password into an Argon2 hash
        password_hash = hash_password(data.password)

        # Create the SQLAlchemy User object
        user = User(

            # Store the user's first name
            first_name=data.first_name.strip(),

            last_name=data.last_name.strip(),

            date_of_birth=data.date_of_birth,

            email=email,

            password_hash=password_hash,

            email_verified=False,

            is_active=True,
        )

        # Save the user in the database
        return await UserRepository.create(
            db,
            user,
        )
