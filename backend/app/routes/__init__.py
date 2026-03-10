from fastapi import APIRouter
from app.routes.auth_routes import router as auth_router
from app.routes.claim_routes import router as claim_router
from app.routes.insurance_routes import router as insurance_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(claim_router, prefix="/claims", tags=["Claims"])
api_router.include_router(insurance_router, prefix="/insurances", tags=["Insurances"])

__all__ = ["api_router"]
