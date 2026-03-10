from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.insurance import Insurance


async def list_insurances(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[Insurance], int]:
    """List all insurances with pagination."""
    # Get total count
    count_query = select(func.count()).select_from(Insurance)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated items
    offset = (page - 1) * page_size
    query = select(Insurance).offset(offset).limit(page_size).order_by(Insurance.id)
    result = await db.execute(query)
    insurances = list(result.scalars().all())

    return insurances, total


async def get_insurance_by_id(
    db: AsyncSession,
    insurance_id: int,
) -> Insurance | None:
    """Get insurance by ID."""
    query = select(Insurance).where(Insurance.id == insurance_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()
