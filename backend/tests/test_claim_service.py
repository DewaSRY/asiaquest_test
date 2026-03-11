import pytest
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.claim_service import (
    create_claim,
    update_claim,
    submit_claim,
    review_claim,
    approve_claim,
    list_claims,
    get_claim_detail,
    delete_claim,
    get_claim_by_id,
    get_claim_by_number,
)
from app.models.user import User, UserRole
from app.models.claim_insurance import ClaimInsurance, ClaimStatus
from app.models.claim_approval import ApprovalDecision
from app.models.insurance import Insurance
from app.dtos.claim import (
    ClaimCreate,
    ClaimUpdate,
    ClaimReviewCreate,
    ClaimApprovalCreate,
    ClaimStatusFilter,
)
from app.errors import NotFoundException, ForbiddenException, BadRequestException
from app.utils.security import hash_password


# ============ Fixtures ============

@pytest.fixture
def claim_create_data(sample_insurance: Insurance) -> ClaimCreate:
    """Create sample claim creation data."""
    return ClaimCreate(insurance_id=sample_insurance.id)


@pytest.fixture
def claim_update_data() -> ClaimUpdate:
    """Create sample claim update data with all required fields for submission."""
    return ClaimUpdate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890",
        user_id_number="ID123456",
        policy_number="POL-001",
        policy_holder_number="PH-001",
        coverage_start_date=date(2025, 1, 1),
        coverage_end_date=date(2026, 1, 1),
        claim_date=date(2026, 3, 1),
        claim_type="Medical",
        description="Medical expense claim",
        claim_amount=Decimal("1000.00"),
    )


# ============ Test Create Claim ============

class TestCreateClaim:
    """Tests for the create_claim function."""

    @pytest.mark.asyncio
    async def test_create_claim_success(
        self,
        db_session: AsyncSession,
        sample_user: User,
        sample_insurance: Insurance,
    ):
        """Test successful claim creation."""
        data = ClaimCreate(insurance_id=sample_insurance.id)
        
        result = await create_claim(db_session, sample_user, data)
        
        assert result is not None
        assert result.id is not None
        assert result.claim_number.startswith("CLM-")
        assert result.user_id == sample_user.id
        assert result.insurance_id == sample_insurance.id
        assert result.status == ClaimStatus.DRAFT


# ============ Test Update Claim ============

class TestUpdateClaim:
    """Tests for the update_claim function."""

    @pytest.mark.asyncio
    async def test_update_claim_success(
        self,
        db_session: AsyncSession,
        sample_user: User,
        sample_draft_claim: ClaimInsurance,
    ):
        """Test successful claim update."""
        update_data = ClaimUpdate(
            first_name="Updated",
            last_name="Name",
            email="updated@example.com",
        )
        
        result = await update_claim(db_session, sample_user, sample_draft_claim.id, update_data)
        
        assert result.first_name == "Updated"
        assert result.last_name == "Name"
        assert result.email == "updated@example.com"

    @pytest.mark.asyncio
    async def test_update_claim_not_found(
        self,
        db_session: AsyncSession,
        sample_user: User,
    ):
        """Test update fails when claim doesn't exist."""
        update_data = ClaimUpdate(first_name="Test")
        
        with pytest.raises(NotFoundException) as exc_info:
            await update_claim(db_session, sample_user, 99999, update_data)
        
        assert "Claim not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_update_claim_not_owner(
        self,
        db_session: AsyncSession,
        sample_draft_claim: ClaimInsurance,
        sample_verifier: User,
    ):
        """Test update fails when user is not the claim owner."""
        update_data = ClaimUpdate(first_name="Test")
        
        with pytest.raises(ForbiddenException) as exc_info:
            await update_claim(db_session, sample_verifier, sample_draft_claim.id, update_data)
        
        assert "You can only update your own claims" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_update_claim_not_draft(
        self,
        db_session: AsyncSession,
        sample_user: User,
        sample_submitted_claim: ClaimInsurance,
    ):
        """Test update fails when claim is not in DRAFT status."""
        update_data = ClaimUpdate(first_name="Test")
        
        with pytest.raises(BadRequestException) as exc_info:
            await update_claim(db_session, sample_user, sample_submitted_claim.id, update_data)
        
        assert "Only DRAFT claims can be updated" in str(exc_info.value.detail)


# ============ Test Submit Claim ============

class TestSubmitClaim:
    """Tests for the submit_claim function."""

    @pytest.mark.asyncio
    async def test_submit_claim_success(
        self,
        db_session: AsyncSession,
        sample_user: User,
        sample_complete_draft_claim: ClaimInsurance,
    ):
        """Test successful claim submission."""
        result = await submit_claim(db_session, sample_user, sample_complete_draft_claim.id)
        
        assert result.status == ClaimStatus.SUBMITTED

    @pytest.mark.asyncio
    async def test_submit_claim_not_found(
        self,
        db_session: AsyncSession,
        sample_user: User,
    ):
        """Test submit fails when claim doesn't exist."""
        with pytest.raises(NotFoundException) as exc_info:
            await submit_claim(db_session, sample_user, 99999)
        
        assert "Claim not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_submit_claim_not_owner(
        self,
        db_session: AsyncSession,
        sample_complete_draft_claim: ClaimInsurance,
        sample_verifier: User,
    ):
        """Test submit fails when user is not the claim owner."""
        with pytest.raises(ForbiddenException) as exc_info:
            await submit_claim(db_session, sample_verifier, sample_complete_draft_claim.id)
        
        assert "You can only submit your own claims" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_submit_claim_not_draft(
        self,
        db_session: AsyncSession,
        sample_user: User,
        sample_submitted_claim: ClaimInsurance,
    ):
        """Test submit fails when claim is not in DRAFT status."""
        with pytest.raises(BadRequestException) as exc_info:
            await submit_claim(db_session, sample_user, sample_submitted_claim.id)
        
        assert "Only DRAFT claims can be submitted" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_submit_claim_missing_required_fields(
        self,
        db_session: AsyncSession,
        sample_user: User,
        sample_draft_claim: ClaimInsurance,
    ):
        """Test submit fails when required fields are missing."""
        with pytest.raises(BadRequestException) as exc_info:
            await submit_claim(db_session, sample_user, sample_draft_claim.id)
        
        assert "Missing required fields" in str(exc_info.value.detail)


# ============ Test Review Claim ============

class TestReviewClaim:
    """Tests for the review_claim function."""

    @pytest.mark.asyncio
    async def test_review_claim_success(
        self,
        db_session: AsyncSession,
        sample_verifier: User,
        sample_submitted_claim: ClaimInsurance,
    ):
        """Test successful claim review."""
        review_data = ClaimReviewCreate(summary="Claim reviewed and verified.")
        
        result = await review_claim(db_session, sample_verifier, sample_submitted_claim.id, review_data)
        
        assert result.status == ClaimStatus.REVIEWED
        
        # Verify the review was created by querying it directly
        from sqlalchemy import select
        from app.models.claim_review import ClaimReview
        review_result = await db_session.execute(
            select(ClaimReview).where(ClaimReview.claim_id == sample_submitted_claim.id)
        )
        review = review_result.scalar_one_or_none()
        assert review is not None
        assert review.summary == "Claim reviewed and verified."
        assert review.verifier_id == sample_verifier.id

    @pytest.mark.asyncio
    async def test_review_claim_not_verifier(
        self,
        db_session: AsyncSession,
        sample_user: User,
        sample_submitted_claim: ClaimInsurance,
    ):
        """Test review fails when user is not a verifier."""
        review_data = ClaimReviewCreate(summary="Claim reviewed and verified.")
        
        with pytest.raises(ForbiddenException) as exc_info:
            await review_claim(db_session, sample_user, sample_submitted_claim.id, review_data)
        
        assert "Only verifiers can review claims" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_review_claim_not_found(
        self,
        db_session: AsyncSession,
        sample_verifier: User,
    ):
        """Test review fails when claim doesn't exist."""
        review_data = ClaimReviewCreate(summary="Claim reviewed and verified.")
        
        with pytest.raises(NotFoundException) as exc_info:
            await review_claim(db_session, sample_verifier, 99999, review_data)
        
        assert "Claim not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_review_claim_not_submitted(
        self,
        db_session: AsyncSession,
        sample_verifier: User,
        sample_draft_claim: ClaimInsurance,
    ):
        """Test review fails when claim is not in SUBMITTED status."""
        review_data = ClaimReviewCreate(summary="Claim reviewed and verified.")
        
        with pytest.raises(BadRequestException) as exc_info:
            await review_claim(db_session, sample_verifier, sample_draft_claim.id, review_data)
        
        assert "Only SUBMITTED claims can be reviewed" in str(exc_info.value.detail)


# ============ Test Approve Claim ============

class TestApproveClaim:
    """Tests for the approve_claim function."""

    @pytest.mark.asyncio
    async def test_approve_claim_success(
        self,
        db_session: AsyncSession,
        sample_approver: User,
        sample_reviewed_claim: ClaimInsurance,
    ):
        """Test successful claim approval."""
        approval_data = ClaimApprovalCreate(
            decision=ApprovalDecision.APPROVED,
            summary="Approved after review.",
        )
        
        result = await approve_claim(db_session, sample_approver, sample_reviewed_claim.id, approval_data)
        
        assert result.status == ClaimStatus.APPROVED
        
        # Verify the approval was created by querying it directly
        from sqlalchemy import select
        from app.models.claim_approval import ClaimApproval
        approval_result = await db_session.execute(
            select(ClaimApproval).where(ClaimApproval.claim_id == sample_reviewed_claim.id)
        )
        approval = approval_result.scalar_one_or_none()
        assert approval is not None
        assert approval.decision == ApprovalDecision.APPROVED
        assert approval.approver_id == sample_approver.id

    @pytest.mark.asyncio
    async def test_reject_claim_success(
        self,
        db_session: AsyncSession,
        sample_approver: User,
        sample_reviewed_claim: ClaimInsurance,
    ):
        """Test successful claim rejection."""
        approval_data = ClaimApprovalCreate(
            decision=ApprovalDecision.REJECTED,
            summary="Rejected due to insufficient documentation.",
        )
        
        result = await approve_claim(db_session, sample_approver, sample_reviewed_claim.id, approval_data)
        
        assert result.status == ClaimStatus.REJECTED
        
        # Verify the approval was created by querying it directly
        from sqlalchemy import select
        from app.models.claim_approval import ClaimApproval
        approval_result = await db_session.execute(
            select(ClaimApproval).where(ClaimApproval.claim_id == sample_reviewed_claim.id)
        )
        approval = approval_result.scalar_one_or_none()
        assert approval is not None
        assert approval.decision == ApprovalDecision.REJECTED

    @pytest.mark.asyncio
    async def test_reject_claim_requires_reason(
        self,
        db_session: AsyncSession,
        sample_approver: User,
        sample_reviewed_claim: ClaimInsurance,
    ):
        """Test rejection fails without a reason."""
        approval_data = ClaimApprovalCreate(
            decision=ApprovalDecision.REJECTED,
            summary=None,
        )
        
        with pytest.raises(BadRequestException) as exc_info:
            await approve_claim(db_session, sample_approver, sample_reviewed_claim.id, approval_data)
        
        assert "Reason is required for rejection" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_approve_claim_not_approver(
        self,
        db_session: AsyncSession,
        sample_verifier: User,
        sample_reviewed_claim: ClaimInsurance,
    ):
        """Test approval fails when user is not an approver."""
        approval_data = ClaimApprovalCreate(
            decision=ApprovalDecision.APPROVED,
            summary="Approved.",
        )
        
        with pytest.raises(ForbiddenException) as exc_info:
            await approve_claim(db_session, sample_verifier, sample_reviewed_claim.id, approval_data)
        
        assert "Only approvers can approve/reject claims" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_approve_claim_not_found(
        self,
        db_session: AsyncSession,
        sample_approver: User,
    ):
        """Test approval fails when claim doesn't exist."""
        approval_data = ClaimApprovalCreate(
            decision=ApprovalDecision.APPROVED,
            summary="Approved.",
        )
        
        with pytest.raises(NotFoundException) as exc_info:
            await approve_claim(db_session, sample_approver, 99999, approval_data)
        
        assert "Claim not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_approve_claim_not_reviewed(
        self,
        db_session: AsyncSession,
        sample_approver: User,
        sample_submitted_claim: ClaimInsurance,
    ):
        """Test approval fails when claim is not in REVIEWED status."""
        approval_data = ClaimApprovalCreate(
            decision=ApprovalDecision.APPROVED,
            summary="Approved.",
        )
        
        with pytest.raises(BadRequestException) as exc_info:
            await approve_claim(db_session, sample_approver, sample_submitted_claim.id, approval_data)
        
        assert "Only REVIEWED claims can be approved/rejected" in str(exc_info.value.detail)


# ============ Test List Claims ============

class TestListClaims:
    """Tests for the list_claims function."""

    @pytest.mark.asyncio
    async def test_list_claims_user_sees_own_claims(
        self,
        db_session: AsyncSession,
        sample_user: User,
        sample_draft_claim: ClaimInsurance,
    ):
        """Test user can only see their own claims."""
        claims, total = await list_claims(db_session, sample_user)
        
        assert total >= 1
        assert all(c.user_id == sample_user.id for c in claims)

    @pytest.mark.asyncio
    async def test_list_claims_verifier_sees_all(
        self,
        db_session: AsyncSession,
        sample_verifier: User,
        sample_draft_claim: ClaimInsurance,
    ):
        """Test verifier can see all claims."""
        claims, total = await list_claims(db_session, sample_verifier)
        
        assert total >= 1

    @pytest.mark.asyncio
    async def test_list_claims_filter_by_status(
        self,
        db_session: AsyncSession,
        sample_verifier: User,
        sample_submitted_claim: ClaimInsurance,
    ):
        """Test filtering claims by status."""
        claims, total = await list_claims(
            db_session,
            sample_verifier,
            status_filter=ClaimStatusFilter.SUBMITTED,
        )
        
        assert all(c.status == ClaimStatus.SUBMITTED for c in claims)

    @pytest.mark.asyncio
    async def test_list_claims_pagination(
        self,
        db_session: AsyncSession,
        sample_verifier: User,
        sample_draft_claim: ClaimInsurance,
    ):
        """Test pagination works correctly."""
        claims, total = await list_claims(
            db_session,
            sample_verifier,
            page=1,
            page_size=5,
        )
        
        assert len(claims) <= 5


# ============ Test Get Claim Detail ============

class TestGetClaimDetail:
    """Tests for the get_claim_detail function."""

    @pytest.mark.asyncio
    async def test_get_claim_detail_owner(
        self,
        db_session: AsyncSession,
        sample_user: User,
        sample_draft_claim: ClaimInsurance,
    ):
        """Test owner can view their claim."""
        result = await get_claim_detail(db_session, sample_user, sample_draft_claim.id)
        
        assert result.id == sample_draft_claim.id

    @pytest.mark.asyncio
    async def test_get_claim_detail_verifier(
        self,
        db_session: AsyncSession,
        sample_verifier: User,
        sample_draft_claim: ClaimInsurance,
    ):
        """Test verifier can view any claim."""
        result = await get_claim_detail(db_session, sample_verifier, sample_draft_claim.id)
        
        assert result.id == sample_draft_claim.id

    @pytest.mark.asyncio
    async def test_get_claim_detail_not_found(
        self,
        db_session: AsyncSession,
        sample_user: User,
    ):
        """Test viewing non-existent claim fails."""
        with pytest.raises(NotFoundException) as exc_info:
            await get_claim_detail(db_session, sample_user, 99999)
        
        assert "Claim not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_claim_detail_user_forbidden(
        self,
        db_session: AsyncSession,
        sample_draft_claim: ClaimInsurance,
        db_session_factory,
    ):
        """Test user cannot view another user's claim."""
        # Create another user
        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password=hash_password("password123"),
            role=UserRole.USER,
        )
        db_session.add(other_user)
        await db_session.flush()
        
        with pytest.raises(ForbiddenException) as exc_info:
            await get_claim_detail(db_session, other_user, sample_draft_claim.id)
        
        assert "You can only view your own claims" in str(exc_info.value.detail)


# ============ Test Delete Claim ============

class TestDeleteClaim:
    """Tests for the delete_claim function."""

    @pytest.mark.asyncio
    async def test_delete_claim_success(
        self,
        db_session: AsyncSession,
        sample_user: User,
        sample_draft_claim: ClaimInsurance,
    ):
        """Test successful claim deletion."""
        claim_id = sample_draft_claim.id
        
        await delete_claim(db_session, sample_user, claim_id)
        
        # Verify claim is deleted
        deleted_claim = await get_claim_by_id(db_session, claim_id)
        assert deleted_claim is None

    @pytest.mark.asyncio
    async def test_delete_claim_not_found(
        self,
        db_session: AsyncSession,
        sample_user: User,
    ):
        """Test delete fails when claim doesn't exist."""
        with pytest.raises(NotFoundException) as exc_info:
            await delete_claim(db_session, sample_user, 99999)
        
        assert "Claim not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_delete_claim_not_owner(
        self,
        db_session: AsyncSession,
        sample_draft_claim: ClaimInsurance,
        sample_verifier: User,
    ):
        """Test delete fails when user is not the owner."""
        with pytest.raises(ForbiddenException) as exc_info:
            await delete_claim(db_session, sample_verifier, sample_draft_claim.id)
        
        assert "You can only delete your own claims" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_delete_claim_not_draft(
        self,
        db_session: AsyncSession,
        sample_user: User,
        sample_submitted_claim: ClaimInsurance,
    ):
        """Test delete fails when claim is not in DRAFT status."""
        with pytest.raises(BadRequestException) as exc_info:
            await delete_claim(db_session, sample_user, sample_submitted_claim.id)
        
        assert "Only DRAFT claims can be deleted" in str(exc_info.value.detail)


# ============ Test Helper Functions ============

class TestHelperFunctions:
    """Tests for helper functions."""

    @pytest.mark.asyncio
    async def test_get_claim_by_id(
        self,
        db_session: AsyncSession,
        sample_draft_claim: ClaimInsurance,
    ):
        """Test get_claim_by_id returns correct claim."""
        result = await get_claim_by_id(db_session, sample_draft_claim.id)
        
        assert result is not None
        assert result.id == sample_draft_claim.id

    @pytest.mark.asyncio
    async def test_get_claim_by_id_not_found(
        self,
        db_session: AsyncSession,
    ):
        """Test get_claim_by_id returns None for non-existent claim."""
        result = await get_claim_by_id(db_session, 99999)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_claim_by_number(
        self,
        db_session: AsyncSession,
        sample_draft_claim: ClaimInsurance,
    ):
        """Test get_claim_by_number returns correct claim."""
        result = await get_claim_by_number(db_session, sample_draft_claim.claim_number)
        
        assert result is not None
        assert result.claim_number == sample_draft_claim.claim_number

    @pytest.mark.asyncio
    async def test_get_claim_by_number_not_found(
        self,
        db_session: AsyncSession,
    ):
        """Test get_claim_by_number returns None for non-existent claim."""
        result = await get_claim_by_number(db_session, "CLM-NONEXISTENT")
        
        assert result is None
