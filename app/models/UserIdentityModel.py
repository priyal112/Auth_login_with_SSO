from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class UserIdentity(Base):

    __tablename__ = "user_identities"

    # Primary key
    identity_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id"),
        nullable=False,
        index=True,
    )

    # Name of the authentication provider
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    # Unique user ID given by the provider
    provider_user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Email returned by the provider
    provider_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    # Prevent the same provider identity from being
    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_user_id",
            name="uq_user_identities_provider_user",
        ),
    )