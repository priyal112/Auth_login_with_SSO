from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # PostgreSQL database connection string
    DATABASE_URL: str

    JWT_SECRET_KEY: str

    JWT_ALGORITHM: str = "HS256"

    # Access token expiration time
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    SMTP_HOST: str

    SMTP_PORT: int = 587

    SMTP_USERNAME: str

    SMTP_PASSWORD: str

    # Email address that appears as the sender
    SMTP_FROM_EMAIL: str

    GOOGLE_CLIENT_ID: str

    GOOGLE_CLIENT_SECRET: str

    GOOGLE_REDIRECT_URI: str

    MICROSOFT_CLIENT_ID: str

    MICROSOFT_CLIENT_SECRET: str

    MICROSOFT_REDIRECT_URI: str

    APP_BASE_URL: str = "http://127.0.0.1:8000"

    # Tell Pydantic to load values from .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Create one settings object for the application
settings = Settings()