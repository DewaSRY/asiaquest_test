from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dtos.insurance import InsuranceResponse, InsuranceListResponse
from app.services import insurance_service

router = APIRouter()


@router.get(
    "",
    response_model=InsuranceListResponse,
    summary="List all insurances",
    description="List all available insurances with pagination.",
)
async def list_insurances(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> InsuranceListResponse:
    """List all available insurances."""
    insurances, total = await insurance_service.list_insurances(db, page, page_size)

    total_pages = (total + page_size - 1) // page_size

    return InsuranceListResponse(
        items=[InsuranceResponse.model_validate(i) for i in insurances],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
