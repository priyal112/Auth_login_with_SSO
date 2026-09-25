from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app import models 
from app.controllers.AuthController import router as auth_router
from app.database.base import Base
from app.database.session import engine


# Run when the application starts and stops
@asynccontextmanager
async def lifespan(app: FastAPI):

    # Create database tables when the application starts

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    # Start the FastAPI application
    yield

    await engine.dispose()


app = FastAPI(
    title="Authentication API",
    lifespan=lifespan,
)


#  routes
app.include_router(auth_router)


@app.get("/")
async def root():

    return {
        "message": "Authentication API is running"
    }


# Database connection test endpoint
@app.get("/database-test")
async def database_test():

    async with engine.connect() as connection:

        # Execute a simple PostgreSQL query
        result = await connection.execute(
            text("SELECT 1")
        )

        return {
            "database": result.scalar()
        }
