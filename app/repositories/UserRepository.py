from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.UserModel import User


class UserRepository:

    # Find a user using their email address
    @staticmethod
    async def get_by_email(
        db: AsyncSession,
        email: str,
    ) -> User | None:

        # Build a query to find the user
        result = await db.execute(
            select(User).where(User.email == email)
        )

        return result.scalar_one_or_none()

    # Create a new user in the database
    @staticmethod
    async def create(
        db: AsyncSession,
        user: User,
    ) -> User:

        # Add the user object to the database session
        db.add(user)

        await db.commit()

        await db.refresh(user)

        return user
    

    # Find a user using their user ID 
    @staticmethod 
    async def get_by_id( 
        db: AsyncSession, 
        user_id: int, 
        ) -> User | None: 

        # Build a query to find the user 
        result = await db.execute( select(User).where(User.user_id == user_id) ) 
        
        return result.scalar_one_or_none()
