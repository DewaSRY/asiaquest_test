from datetime import datetime
from sqlalchemy import DateTime, Text, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Insurance(Base):
    """Insurance model - created by Verifier."""

    __tablename__ = "insurance"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    claims = relationship("ClaimInsurance", back_populates="insurance")

    def __repr__(self) -> str:
        return f"<Insurance(id={self.id}, number={self.number}, title={self.title}, description={self.description} )>"
