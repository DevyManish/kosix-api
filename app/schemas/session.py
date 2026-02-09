from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


# Base schema with common fields
class SessionBase(BaseModel):
    """Base session schema with common fields."""
    ip_address: Optional[str] = None


# Schema for creating a session
class SessionCreate(SessionBase):
    """Schema for creating a new session."""
    account_id: UUID
    session_token: str
    expires_at: datetime


# Schema for session response
class SessionResponse(SessionBase):
    """Schema for session response."""
    id: UUID
    account_id: UUID
    session_token: str
    expires_at: datetime
    created_at: datetime
    is_active: bool

    model_config = {"from_attributes": True}


# Schema for session list item
class SessionListItem(BaseModel):
    """Schema for session in list responses."""
    id: UUID
    created_at: datetime
    expires_at: datetime
    ip_address: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}


# Schema for token response
class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime


# Schema for token with user info
class AuthResponse(BaseModel):
    """Schema for authentication response with user info."""
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: "AccountResponse"

    model_config = {"from_attributes": True}


# Import at the end to avoid circular imports
from app.schemas.account import AccountResponse  # noqa: E402
AuthResponse.model_rebuild()
