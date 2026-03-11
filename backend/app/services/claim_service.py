import uuid
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, UserRole
from app.models.claim_insurance import ClaimInsurance, ClaimStatus
from app.models.claim_review import ClaimReview
from app.models.claim_approval import ClaimApproval, ApprovalDecision
from app.dtos.claim import (
    ClaimCreate,
    ClaimUpdate,
    ClaimReviewCreate,
    ClaimApprovalCreate,
    ClaimStatusFilter,
)
from app.errors import (
    NotFoundException,
    ForbiddenException,
    BadRequestException,
)


def _generate_claim_number() -> str:
    """Generate unique claim number."""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:6].upper()
    return f"CLM-{timestamp}-{unique_id}"


async def get_claim_by_id(
    db: AsyncSession,
    claim_id: int,
    with_relations: bool = False,
) -> ClaimInsurance | None:
    """Get claim by ID, optionally with review and approval."""
    query = select(ClaimInsurance).where(ClaimInsurance.id == claim_id)
    
    if with_relations:
        query = query.options(
            selectinload(ClaimInsurance.review),
            selectinload(ClaimInsurance.approval),
        )
    
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_claim_by_number(
    db: AsyncSession,
    claim_number: str,
    with_relations: bool = False,
) -> ClaimInsurance | None:
    """Get claim by claim number."""
    query = select(ClaimInsurance).where(ClaimInsurance.claim_number == claim_number)
    
    if with_relations:
        query = query.options(
            selectinload(ClaimInsurance.review),
            selectinload(ClaimInsurance.approval),
        )
    
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_claim(
    db: AsyncSession,
    user: User,
    data: ClaimCreate,
) -> ClaimInsurance:
    """Create a new claim in DRAFT status."""
    claim = ClaimInsurance(
        claim_number=_generate_claim_number(),
        user_id=user.id,
        insurance_id=data.insurance_id,
        status=ClaimStatus.DRAFT,
    )
    
    db.add(claim)
    await db.flush()
    await db.refresh(claim)
    return claim


async def update_claim(
    db: AsyncSession,
    user: User,
    claim_id: int,
    data: ClaimUpdate,
) -> ClaimInsurance:
    """Update a draft claim. Only owner can update, only DRAFT status allowed."""
    claim = await get_claim_by_id(db, claim_id, with_relations=True)
    
    if not claim:
        raise NotFoundException(detail="Claim not found")
    
    # Only owner can update their claim
    if claim.user_id != user.id:
        raise ForbiddenException(detail="You can only update your own claims")
    
    # Only draft claims can be updated
    if claim.status != ClaimStatus.DRAFT:
        raise BadRequestException(
            detail=f"Cannot update claim with status '{claim.status.value}'. Only DRAFT claims can be updated."
        )
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(claim, field, value)
    
    await db.flush()
    await db.refresh(claim)
    return claim


async def submit_claim(
    db: AsyncSession,
    user: User,
    claim_id: int,
) -> ClaimInsurance:
    """Submit a draft claim for review. DRAFT → SUBMITTED."""
    claim = await get_claim_by_id(db, claim_id, with_relations=True)
    
    if not claim:
        raise NotFoundException(detail="Claim not found")
    
    if claim.user_id != user.id:
        raise ForbiddenException(detail="You can only submit your own claims")
    
    if claim.status != ClaimStatus.DRAFT:
        raise BadRequestException(
            detail=f"Cannot submit claim with status '{claim.status.value}'. Only DRAFT claims can be submitted."
        )
    
    # Validate required fields before submission
    required_fields = ["first_name", "last_name", "email", "policy_number", "claim_amount"]
    missing = [f for f in required_fields if not getattr(claim, f)]
    if missing:
        raise BadRequestException(
            detail=f"Missing required fields for submission: {', '.join(missing)}"
        )
    
    claim.status = ClaimStatus.SUBMITTED
    await db.flush()
    await db.refresh(claim)
    return claim


async def review_claim(
    db: AsyncSession,
    verifier: User,
    claim_id: int,
    data: ClaimReviewCreate,
) -> ClaimInsurance:
    """Verifier reviews a submitted claim. SUBMITTED → REVIEWED."""
    if verifier.role not in [UserRole.VERIFIER, UserRole.APPROVER]:
        raise ForbiddenException(detail="Only verifiers can review claims")
    
    claim = await get_claim_by_id(db, claim_id, with_relations=True)
    
    if not claim:
        raise NotFoundException(detail="Claim not found")
    
    if claim.status != ClaimStatus.SUBMITTED:
        raise BadRequestException(
            detail=f"Cannot review claim with status '{claim.status.value}'. Only SUBMITTED claims can be reviewed."
        )
    
    # Create review record
    review = ClaimReview(
        claim_id=claim.id,
        verifier_id=verifier.id,
        summary=data.summary,
        reviewed_at=datetime.utcnow(),
    )
    db.add(review)
    
    # Update claim status
    claim.status = ClaimStatus.REVIEWED
    await db.flush()
    
    # Reload with relations
    claim = await get_claim_by_id(db, claim_id, with_relations=True)
    return claim


async def approve_claim(
    db: AsyncSession,
    approver: User,
    claim_id: int,
    data: ClaimApprovalCreate,
) -> ClaimInsurance:
    """Approver approves/rejects a reviewed claim. REVIEWED → APPROVED/REJECTED."""
    if approver.role != UserRole.APPROVER:
        raise ForbiddenException(detail="Only approvers can approve/reject claims")
    
    claim = await get_claim_by_id(db, claim_id, with_relations=True)
    
    if not claim:
        raise NotFoundException(detail="Claim not found")
    
    if claim.status != ClaimStatus.REVIEWED:
        raise BadRequestException(
            detail=f"Cannot approve/reject claim with status '{claim.status.value}'. Only REVIEWED claims can be approved/rejected."
        )
    
    # Require summary for rejection
    if data.decision == ApprovalDecision.REJECTED and not data.summary:
        raise BadRequestException(detail="Summary is required for rejection")
    
    # Create approval record
    approval = ClaimApproval(
        claim_id=claim.id,
        approver_id=approver.id,
        decision=data.decision,
        summary=data.summary,
        decided_at=datetime.utcnow(),
    )
    db.add(approval)
    
    # Update claim status based on decision
    claim.status = (
        ClaimStatus.APPROVED if data.decision == ApprovalDecision.APPROVED
        else ClaimStatus.REJECTED
    )
    await db.flush()
    
    # Reload with relations
    claim = await get_claim_by_id(db, claim_id, with_relations=True)
    return claim


async def list_claims(
    db: AsyncSession,
    user: User,
    status_filter: ClaimStatusFilter = ClaimStatusFilter.ALL,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[ClaimInsurance], int]:
    """
    List claims with pagination.
    - Users see only their own claims
    - Verifiers/Approvers see all claims
    """
    query = select(ClaimInsurance).options(
        selectinload(ClaimInsurance.review),
        selectinload(ClaimInsurance.approval),
    )
    count_query = select(func.count(ClaimInsurance.id))
    
    # Filter by user role
    if user.role == UserRole.USER:
        query = query.where(ClaimInsurance.user_id == user.id)
        count_query = count_query.where(ClaimInsurance.user_id == user.id)
    
    # Filter by status
    if status_filter != ClaimStatusFilter.ALL:
        status_value = ClaimStatus(status_filter.value)
        query = query.where(ClaimInsurance.status == status_value)
        count_query = count_query.where(ClaimInsurance.status == status_value)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # Pagination
    offset = (page - 1) * page_size
    query = query.order_by(ClaimInsurance.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    claims = list(result.scalars().all())
    
    return claims, total


async def get_claim_detail(
    db: AsyncSession,
    user: User,
    claim_id: int,
) -> ClaimInsurance:
    """
    Get claim detail.
    - Users can only see their own claims
    - Verifiers/Approvers can see all claims
    """
    claim = await get_claim_by_id(db, claim_id, with_relations=True)
    
    if not claim:
        raise NotFoundException(detail="Claim not found")
    
    # Users can only view their own claims
    if user.role == UserRole.USER and claim.user_id != user.id:
        raise ForbiddenException(detail="You can only view your own claims")
    
    return claim


async def delete_claim(
    db: AsyncSession,
    user: User,
    claim_id: int,
) -> None:
    """Delete a draft claim. Only owner can delete, only DRAFT status allowed."""
    claim = await get_claim_by_id(db, claim_id)
    
    if not claim:
        raise NotFoundException(detail="Claim not found")
    
    if claim.user_id != user.id:
        raise ForbiddenException(detail="You can only delete your own claims")
    
    if claim.status != ClaimStatus.DRAFT:
        raise BadRequestException(
            detail=f"Cannot delete claim with status '{claim.status.value}'. Only DRAFT claims can be deleted."
        )
    
    await db.delete(claim)
    await db.flush()
