from datetime import datetime
from enum import Enum
from sqlalchemy import DateTime, Text, ForeignKey, BigInteger, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ApprovalDecision(str, Enum):
    """Approval decision enum."""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ClaimApproval(Base):
    """Claim Approval model - created by Approver."""

    __tablename__ = "claim_approvals"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    claim_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("claim_insurances.id"), nullable=False, unique=True
    )
    approver_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    decision: Mapped[ApprovalDecision] = mapped_column(SQLEnum(ApprovalDecision), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    claim = relationship("ClaimInsurance", back_populates="approval")
    approver = relationship("User", back_populates="approvals")

    def __repr__(self) -> str:
        return f"<ClaimApproval(id={self.id}, claim_id={self.claim_id}, decision={self.decision})>"
