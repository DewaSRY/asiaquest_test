import pytest
import pytest_asyncio
from datetime import datetime, UTC
from decimal import Decimal
from datetime import date
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncConnection,
)
from sqlalchemy.pool import NullPool

from app.database import Base
from app.config import get_settings
from app.models.user import User, UserRole
from app.models.insurance import Insurance
from app.models.claim_insurance import ClaimInsurance, ClaimStatus
from app.models.claim_review import ClaimReview
from app.dtos.auth import UserCreate
from app.utils.security import hash_password

settings = get_settings()

# Create test engine with NullPool to avoid connection pooling issues
test_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool,  # Disable pooling for tests
)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def setup_database():
    """Create database tables and clean test data once per test session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Import models needed for cleanup
    from app.models.claim_approval import ClaimApproval
    
    # Clean up any leftover test data from previous runs
    # We need to delete in correct order due to foreign key constraints
    async with test_engine.begin() as conn:
        async_session = async_sessionmaker(
            bind=conn,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        async with async_session() as session:
            test_emails = [
                "test@example.com",
                "newuser@example.com",
                "verifier@example.com",
                "approver@example.com",
                "other@example.com",
            ]
            
            # Get IDs of test users
            result = await session.execute(
                select(User.id).where(User.email.in_(test_emails))
            )
            test_user_ids = [row[0] for row in result.fetchall()]
            
            if test_user_ids:
                # Get claim IDs for test users
                result = await session.execute(
                    select(ClaimInsurance.id).where(
                        ClaimInsurance.user_id.in_(test_user_ids)
                    )
                )
                test_claim_ids = [row[0] for row in result.fetchall()]
                
                if test_claim_ids:
                    # Delete approvals for test claims
                    await session.execute(
                        delete(ClaimApproval).where(
                            ClaimApproval.claim_id.in_(test_claim_ids)
                        )
                    )
                    
                    # Delete reviews for test claims
                    await session.execute(
                        delete(ClaimReview).where(
                            ClaimReview.claim_id.in_(test_claim_ids)
                        )
                    )
                    
                    # Delete test claims
                    await session.execute(
                        delete(ClaimInsurance).where(
                            ClaimInsurance.id.in_(test_claim_ids)
                        )
                    )
                
                # Also delete reviews created by test verifiers
                await session.execute(
                    delete(ClaimReview).where(
                        ClaimReview.verifier_id.in_(test_user_ids)
                    )
                )
                
                # Also delete approvals created by test approvers
                await session.execute(
                    delete(ClaimApproval).where(
                        ClaimApproval.approver_id.in_(test_user_ids)
                    )
                )
                
                # Delete test users
                await session.execute(
                    delete(User).where(User.id.in_(test_user_ids))
                )
            
            # Delete test insurances
            await session.execute(
                delete(Insurance).where(Insurance.number == "INS-001")
            )
            
            await session.commit()
    
    yield


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_database):
    """
    Create a database session with transaction rollback for testing.
    
    Each test runs within a transaction that is rolled back after the test,
    ensuring test isolation and no persistent data changes.
    """
    # Create a new connection for this test
    connection: AsyncConnection = await test_engine.connect()
    
    # Start a transaction that we'll rollback
    transaction = await connection.begin()
    
    # Create session bound to this connection
    async_session = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    session = async_session()
    
    try:
        yield session
    finally:
        await session.close()
        # Rollback the transaction - this undoes all changes made during the test
        await transaction.rollback()
        await connection.close()


@pytest.fixture
def db_session_factory():
    """Factory fixture marker for tests that need to create additional entities."""
    return True


# ============ User Fixtures ============

@pytest_asyncio.fixture
async def sample_user(db_session: AsyncSession):
    """Create a sample user in the database for testing."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hash_password("password123"),
        role=UserRole.USER,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_verifier(db_session: AsyncSession):
    """Create a sample verifier user for testing."""
    user = User(
        email="verifier@example.com",
        username="verifier",
        hashed_password=hash_password("password123"),
        role=UserRole.VERIFIER,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_approver(db_session: AsyncSession):
    """Create a sample approver user for testing."""
    user = User(
        email="approver@example.com",
        username="approver",
        hashed_password=hash_password("password123"),
        role=UserRole.APPROVER,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest.fixture
def user_create_data():
    """Create sample user registration data."""
    return UserCreate(
        email="newuser@example.com",
        username="newuser",
        password="securepassword123",
    )


# ============ Insurance Fixtures ============

@pytest_asyncio.fixture
async def sample_insurance(db_session: AsyncSession):
    """Create a sample insurance for testing."""
    insurance = Insurance(
        number="INS-001",
        title="Health Insurance",
        description="Basic health insurance coverage",
    )
    db_session.add(insurance)
    await db_session.flush()
    await db_session.refresh(insurance)
    return insurance


# ============ Claim Fixtures ============

@pytest_asyncio.fixture
async def sample_draft_claim(
    db_session: AsyncSession,
    sample_user: User,
    sample_insurance: Insurance,
):
    """Create a sample draft claim for testing."""
    claim = ClaimInsurance(
        claim_number="CLM-TEST-DRAFT-001",
        user_id=sample_user.id,
        insurance_id=sample_insurance.id,
        status=ClaimStatus.DRAFT,
    )
    db_session.add(claim)
    await db_session.flush()
    await db_session.refresh(claim)
    return claim


@pytest_asyncio.fixture
async def sample_complete_draft_claim(
    db_session: AsyncSession,
    sample_user: User,
    sample_insurance: Insurance,
):
    """Create a sample draft claim with all required fields for submission."""
    claim = ClaimInsurance(
        claim_number="CLM-TEST-COMPLETE-001",
        user_id=sample_user.id,
        insurance_id=sample_insurance.id,
        status=ClaimStatus.DRAFT,
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
    db_session.add(claim)
    await db_session.flush()
    await db_session.refresh(claim)
    return claim


@pytest_asyncio.fixture
async def sample_submitted_claim(
    db_session: AsyncSession,
    sample_user: User,
    sample_insurance: Insurance,
):
    """Create a sample submitted claim for testing."""
    claim = ClaimInsurance(
        claim_number="CLM-TEST-SUBMITTED-001",
        user_id=sample_user.id,
        insurance_id=sample_insurance.id,
        status=ClaimStatus.SUBMITTED,
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
    db_session.add(claim)
    await db_session.flush()
    await db_session.refresh(claim)
    return claim


@pytest_asyncio.fixture
async def sample_reviewed_claim(
    db_session: AsyncSession,
    sample_user: User,
    sample_insurance: Insurance,
    sample_verifier: User,
):
    """Create a sample reviewed claim for testing."""
    claim = ClaimInsurance(
        claim_number="CLM-TEST-REVIEWED-001",
        user_id=sample_user.id,
        insurance_id=sample_insurance.id,
        status=ClaimStatus.REVIEWED,
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
    db_session.add(claim)
    await db_session.flush()
    
    # Create review record
    review = ClaimReview(
        claim_id=claim.id,
        verifier_id=sample_verifier.id,
        summary="Claim verified and ready for approval.",
        reviewed_at=datetime.utcnow(),
    )
    db_session.add(review)
    await db_session.flush()
    await db_session.refresh(claim)
    return claim
