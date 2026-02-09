from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class AuthProvider(str, Enum):
    """Authentication provider types."""
    EMAIL = "email"
    GOOGLE = "google"


class AccountRole(str, Enum):
    """Account role types."""
    OWNER = "owner"
    MANAGER = "manager"
    ADMIN = "admin"
    USER = "user"


# Base schema with common fields
class AccountBase(BaseModel):
    """Base account schema with common fields."""
    email: EmailStr
    name: Optional[str] = None
    username: str = Field(..., min_length=3, max_length=100)
    role: AccountRole = AccountRole.USER
    avatar_url: Optional[str] = None


# Schema for creating an account
class AccountCreate(AccountBase):
    """Schema for creating a new account."""
    provider: AuthProvider = AuthProvider.EMAIL
    provider_account_id: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


# Schema for updating an account
class AccountUpdate(BaseModel):
    """Schema for updating an account."""
    name: Optional[str] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    avatar_url: Optional[str] = None
    role: Optional[AccountRole] = None
    email_verified: Optional[bool] = None


# Schema for account response
class AccountResponse(AccountBase):
    """Schema for account response."""
    id: UUID
    provider: AuthProvider
    email_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Schema for account in list responses
class AccountListItem(BaseModel):
    """Schema for account in list responses."""
    id: UUID
    email: EmailStr
    name: Optional[str] = None
    username: str
    role: AccountRole
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


# Schema for login request
class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str


# Schema for registration request
class RegisterRequest(BaseModel):
    """Schema for registration request."""
    email: EmailStr
    name: Optional[str] = None
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)


# Schema for Google OAuth
class GoogleAuthRequest(BaseModel):
    """Schema for Google OAuth authentication."""
    token: str
