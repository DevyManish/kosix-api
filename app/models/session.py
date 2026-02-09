import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, DateTime, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Session(Base):
    """
    Session model for managing user authentication sessions.
    Tracks active sessions with token and expiration.
    """
    __tablename__ = "sessions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    session_token = Column(
        String(500),
        unique=True,
        nullable=False,
        index=True
    )
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    ip_address = Column(String(45), nullable=True)  # Supports IPv6
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    account = relationship(
        "Account",
        back_populates="sessions"
    )

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, account_id={self.account_id}, is_active={self.is_active})>"

    @property
    def is_expired(self) -> bool:
        """Check if the session has expired."""
        return datetime.utcnow() > self.expires_at
