from pydantic import BaseModel, Field


class InsuranceResponse(BaseModel):
    """DTO for insurance response."""

    id: int
    number: str
    title: str
    description: str | None = None

    class Config:
        from_attributes = True


class InsuranceListResponse(BaseModel):
    """DTO for paginated insurance list response."""

    items: list[InsuranceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
