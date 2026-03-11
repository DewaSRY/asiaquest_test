from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, EmailStr, Field

from app.models.claim_insurance import ClaimStatus
from app.models.claim_approval import ApprovalDecision


# ============ Request DTOs ============

class ClaimCreate(BaseModel):
    """DTO for creating a new claim (creates DRAFT)."""
    insurance_id: int = Field(..., description="insurance id want to claim")



class ClaimUpdate(BaseModel):
    """DTO for updating a draft claim (patchable fields)."""
    # User info
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    email: EmailStr | None = None
    phone_number: str | None = Field(None, max_length=20)
    user_id_number: str | None = Field(None, max_length=50)
    
    # Insurance info
    policy_number: str | None = Field(None, max_length=50)
    policy_holder_number: str | None = Field(None, max_length=50)
    coverage_start_date: date | None = None
    coverage_end_date: date | None = None
    
    # Claim details
    claim_date: date | None = None
    claim_type: str | None = Field(None, max_length=100)
    description: str | None = None
    claim_amount: Decimal | None = Field(None, ge=0, decimal_places=2)


class ClaimReviewCreate(BaseModel):
    """DTO for verifier to review a claim."""
    summary: str = Field(..., min_length=10, description="Review summary by verifier")


class ClaimApprovalCreate(BaseModel):
    """DTO for approver to approve/reject a claim."""
    decision: ApprovalDecision
    summary: str | None = Field(None, description="Reason for decision (required for rejection)")


# ============ Response DTOs ============

class ClaimReviewResponse(BaseModel):
    """DTO for claim review response."""
    id: int
    claim_id: int
    verifier_id: int
    review_summary: str
    reviewed_at: datetime
    
    class Config:
        from_attributes = True


class ClaimApprovalResponse(BaseModel):
    """DTO for claim approval response."""
    id: int
    claim_id: int
    approver_id: int
    decision: ApprovalDecision
    reason: str | None
    decided_at: datetime
    
    class Config:
        from_attributes = True


class ClaimResponse(BaseModel):
    """DTO for claim response."""
    id: int
    claim_number: str
    user_id: int
    insurance_id: int
    status: ClaimStatus
    
    # User info
    first_name: str | None
    last_name: str | None
    email: str | None
    phone_number: str | None
    user_id_number: str | None
    
    # Insurance info
    policy_number: str | None
    policy_holder_number: str | None
    coverage_start_date: date | None
    coverage_end_date: date | None
    
    # Claim details
    claim_date: date | None
    claim_type: str | None
    description: str | None
    claim_amount: Decimal | None
    
    created_at: datetime
    updated_at: datetime
    
    # Related data (optional)
    review: ClaimReviewResponse | None = None
    approval: ClaimApprovalResponse | None = None
    
    class Config:
        from_attributes = True


class ClaimListResponse(BaseModel):
    """DTO for paginated claim list."""
    items: list[ClaimResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ClaimStatusFilter(str, Enum):
    """Filter options for claim status."""
    ALL = "all"
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
