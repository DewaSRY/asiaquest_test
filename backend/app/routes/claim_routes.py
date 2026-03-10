from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.dtos.claim import (
    ClaimCreate,
    ClaimUpdate,
    ClaimResponse,
    ClaimListResponse,
    ClaimReviewCreate,
    ClaimApprovalCreate,
    ClaimStatusFilter,
)
from app.services import claim_service
from app.utils.auth import require_auth, require_roles

router = APIRouter()


@router.post(
    "",
    response_model=ClaimResponse,
    status_code=201,
    summary="Create a new claim",
    description="Create a new insurance claim in DRAFT status. Only authenticated users can create claims.",
)
async def create_claim(
    data: ClaimCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
) -> ClaimResponse:
    """Create a new claim."""
    claim = await claim_service.create_claim(db, current_user, data)
    return ClaimResponse.model_validate(claim)


@router.get(
    "",
    response_model=ClaimListResponse,
    summary="List claims",
    description="List claims with pagination. Users see only their claims, verifiers/approvers see all.",
)
async def list_claims(
    status: ClaimStatusFilter = Query(ClaimStatusFilter.ALL, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
) -> ClaimListResponse:
    """List claims with pagination and filters."""
    claims, total = await claim_service.list_claims(
        db, current_user, status, page, page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return ClaimListResponse(
        items=[ClaimResponse.model_validate(c) for c in claims],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{claim_id}",
    response_model=ClaimResponse,
    summary="Get claim detail",
    description="Get detailed information about a specific claim.",
)
async def get_claim(
    claim_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
) -> ClaimResponse:
    """Get claim by ID."""
    claim = await claim_service.get_claim_detail(db, current_user, claim_id)
    return ClaimResponse.model_validate(claim)


@router.patch(
    "/{claim_id}",
    response_model=ClaimResponse,
    summary="Update a draft claim",
    description="Update claim details. Only the owner can update, and only DRAFT claims can be modified.",
)
async def update_claim(
    claim_id: int,
    data: ClaimUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
) -> ClaimResponse:
    """Update a draft claim."""
    claim = await claim_service.update_claim(db, current_user, claim_id, data)
    return ClaimResponse.model_validate(claim)


@router.post(
    "/{claim_id}/submit",
    response_model=ClaimResponse,
    summary="Submit a claim",
    description="Submit a draft claim for review. Changes status from DRAFT to SUBMITTED.",
)
async def submit_claim(
    claim_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
) -> ClaimResponse:
    """Submit a claim for review."""
    claim = await claim_service.submit_claim(db, current_user, claim_id)
    return ClaimResponse.model_validate(claim)


@router.post(
    "/{claim_id}/review",
    response_model=ClaimResponse,
    summary="Review a claim (Verifier)",
    description="Verifier reviews a submitted claim. Changes status from SUBMITTED to REVIEWED.",
)
async def review_claim(
    claim_id: int,
    data: ClaimReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.VERIFIER, UserRole.APPROVER])),
) -> ClaimResponse:
    """Review a submitted claim."""
    claim = await claim_service.review_claim(db, current_user, claim_id, data)
    return ClaimResponse.model_validate(claim)


@router.post(
    "/{claim_id}/approve",
    response_model=ClaimResponse,
    summary="Approve/Reject a claim (Approver)",
    description="Approver approves or rejects a reviewed claim. Changes status from REVIEWED to APPROVED/REJECTED.",
)
async def approve_claim(
    claim_id: int,
    data: ClaimApprovalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.APPROVER])),
) -> ClaimResponse:
    """Approve or reject a reviewed claim."""
    claim = await claim_service.approve_claim(db, current_user, claim_id, data)
    return ClaimResponse.model_validate(claim)


@router.delete(
    "/{claim_id}",
    status_code=204,
    summary="Delete a draft claim",
    description="Delete a draft claim. Only the owner can delete, and only DRAFT claims can be removed.",
)
async def delete_claim(
    claim_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
) -> None:
    """Delete a draft claim."""
    await claim_service.delete_claim(db, current_user, claim_id)
