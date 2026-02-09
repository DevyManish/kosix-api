import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, ForeignKey, Table, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


# Association table for team members (many-to-many)
team_members = Table(
    "team_members",
    Base.metadata,
    Column(
        "team_id",
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "account_id",
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "joined_at",
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
)


# Association table for team managers (many-to-many)
team_managers = Table(
    "team_managers",
    Base.metadata,
    Column(
        "team_id",
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "account_id",
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "assigned_at",
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
)


class Team(Base):
    """
    Team model representing groups/teams.
    Each team has an owner, can have multiple managers and members.
    """
    __tablename__ = "teams"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    name = Column(String(255), nullable=False)
    avatar_url = Column(Text, nullable=True)
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True
    )
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
    owner = relationship(
        "Account",
        back_populates="owned_teams",
        foreign_keys=[owner_id]
    )
    members = relationship(
        "Account",
        secondary=team_members,
        backref="teams",
        lazy="dynamic"
    )
    managers = relationship(
        "Account",
        secondary=team_managers,
        backref="managed_teams",
        lazy="dynamic"
    )

    def __repr__(self) -> str:
        return f"<Team(id={self.id}, name={self.name})>"
