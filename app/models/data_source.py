import uuid
import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, ForeignKey, Text
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


class DataSourceType(str, enum.Enum):
    """Data source type enumeration."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    ORACLE = "oracle"


class DataSourceStatus(str, enum.Enum):
    """Data source status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"


class DataSource(Base):
    """
    DataSource model for managing database connections.
    Supports PostgreSQL, MySQL, and Oracle databases.
    """
    __tablename__ = "data_sources"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    title = Column(String(255), unique=True, nullable=False, index=True)
    type = Column(
        String(50),
        nullable=False
    )
    status = Column(
        String(50),
        nullable=False,
        default=DataSourceStatus.PENDING.value
    )
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    team_id = Column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    config = Column(JSONB, nullable=False)
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
    creator = relationship("Account", backref="data_sources")
    team = relationship("Team", backref="data_sources")
