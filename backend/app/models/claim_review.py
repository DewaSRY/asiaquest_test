from datetime import datetime
from sqlalchemy import DateTime, Text, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ClaimReview(Base):
    """Claim Review model - created by Verifier."""

    __tablename__ = "claim_reviews"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    claim_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("claim_insurances.id"), nullable=False, unique=True
    )
    verifier_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    review_summary: Mapped[str] = mapped_column(Text, nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    claim = relationship("ClaimInsurance", back_populates="review")
    verifier = relationship("User", back_populates="reviews")

    def __repr__(self) -> str:
        return f"<ClaimReview(id={self.id}, claim_id={self.claim_id})>"
