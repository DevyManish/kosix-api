import uuid
from datetime import datetime, timedelta
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class OTP(Base):
    """
    OTP model for storing email verification codes.
    """
    __tablename__ = "otps"

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
    email = Column(String(255), nullable=False, index=True)
    otp_code = Column(String(6), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    account = relationship("Account", backref="otps")

    @classmethod
    def generate_otp(cls, account_id: uuid.UUID, email: str, expires_minutes: int = 10) -> "OTP":
        """Generate a new OTP for an account."""
        import random
        otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        return cls(
            account_id=account_id,
            email=email,
            otp_code=otp_code,
            expires_at=datetime.utcnow() + timedelta(minutes=expires_minutes)
        )

    def is_valid(self) -> bool:
        """Check if OTP is valid (not used and not expired)."""
        return not self.is_used and datetime.utcnow() < self.expires_at
