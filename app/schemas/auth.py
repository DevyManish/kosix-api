from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str = Field(..., min_length=8)


class RegisterRequest(BaseModel):
    """Schema for registration request."""
    email: EmailStr
    name: Optional[str] = None
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)


class GoogleAuthRequest(BaseModel):
    """Schema for Google OAuth authentication."""
    token: str


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8)


class PasswordChangeRequest(BaseModel):
    """Schema for password change request."""
    current_password: str
    new_password: str = Field(..., min_length=8)


class EmailVerificationRequest(BaseModel):
    """Schema for email verification request."""
    token: str
