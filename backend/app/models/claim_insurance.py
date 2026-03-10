from datetime import datetime
from enum import Enum
from sqlalchemy import String, DateTime, Enum as SQLEnum, Text, Numeric, Date, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ClaimStatus(str, Enum):
    """Claim status enum."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"


class ClaimInsurance(Base):
    """Claim Insurance model."""

    __tablename__ = "claim_insurances"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    claim_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    insurance_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("insurances.id"), nullable=False)
    status: Mapped[ClaimStatus] = mapped_column(
        SQLEnum(ClaimStatus), default=ClaimStatus.DRAFT, nullable=False
    )

    # Claim details
    claim_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    claim_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    claim_amount: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)

    # User info (patchable)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    user_id_number: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Insurance info (patchable)
    policy_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    policy_holder_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    coverage_start_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    coverage_end_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user = relationship("User", back_populates="claims")
    review = relationship("ClaimReview", back_populates="claim", uselist=False)
    approval = relationship("ClaimApproval", back_populates="claim", uselist=False)
    insurance = relationship("Insurance", back_populates="claims", uselist=False)

    def __repr__(self) -> str:
        return f"<ClaimInsurance(id={self.id}, claim_number={self.claim_number}, status={self.status})>"
