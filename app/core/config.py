from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database connection string.
    DATABASE_URL: str

    # Secret key used for creating and verifying JWT tokens.
    JWT_SECRET_KEY: str

    # Algorithm used for JWT.
    JWT_ALGORITHM: str = "HS256"

    # How long an access token should remain valid.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Tell Pydantic Settings to read values from the .env file.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Create one settings object that can be imported
# anywhere in our application.
settings = Settings()
