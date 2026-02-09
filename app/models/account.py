import uuid
import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, DateTime, Enum, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class AuthProvider(str, enum.Enum):
    """Authentication provider types."""
    EMAIL = "email"
    GOOGLE = "google"


class AccountRole(str, enum.Enum):
    """Account role types."""
    OWNER = "owner"
    MANAGER = "manager"
    ADMIN = "admin"
    USER = "user"


class Account(Base):
    """
    Account model representing user accounts.
    Supports multiple authentication providers.
    """
    __tablename__ = "accounts"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    provider = Column(
        Enum(AuthProvider, name="auth_provider"),
        nullable=False,
        default=AuthProvider.EMAIL
    )
    provider_account_id = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    role = Column(
        Enum(AccountRole, name="account_role"),
        nullable=False,
        default=AccountRole.USER
    )
    avatar_url = Column(Text, nullable=True)
    password_hash = Column(String(255), nullable=True)
    email_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    sessions = relationship(
        "Session",
        back_populates="account",
        cascade="all, delete-orphan"
    )
    owned_teams = relationship(
        "Team",
        back_populates="owner",
        foreign_keys="Team.owner_id"
    )

    def __repr__(self) -> str:
        return f"<Account(id={self.id}, email={self.email}, username={self.username})>"
