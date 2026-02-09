from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.account import AccountListItem


# Base schema with common fields
class TeamBase(BaseModel):
    """Base team schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    avatar_url: Optional[str] = None


# Schema for creating a team
class TeamCreate(TeamBase):
    """Schema for creating a new team."""
    pass


# Schema for updating a team
class TeamUpdate(BaseModel):
    """Schema for updating a team."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    avatar_url: Optional[str] = None


# Schema for team response (basic)
class TeamResponse(TeamBase):
    """Schema for team response."""
    id: UUID
    owner_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Schema for team response with details
class TeamDetailResponse(TeamResponse):
    """Schema for team response with full details."""
    owner: Optional[AccountListItem] = None
    members: List[AccountListItem] = []
    managers: List[AccountListItem] = []

    model_config = {"from_attributes": True}


# Schema for adding/removing team members
class TeamMemberAction(BaseModel):
    """Schema for adding or removing team members."""
    account_ids: List[UUID]


# Schema for team in list responses
class TeamListItem(BaseModel):
    """Schema for team in list responses."""
    id: UUID
    name: str
    avatar_url: Optional[str] = None
    owner_id: Optional[UUID] = None
    member_count: int = 0

    model_config = {"from_attributes": True}
