from typing import Callable
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.services.auth_service import get_current_user
from app.errors import ForbiddenException

bearer_scheme = HTTPBearer()


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    return await get_current_user(db, credentials.credentials)


# def require_role(role: UserRole) -> Callable:
#     async def role_checker(
#         credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
#         db: AsyncSession = Depends(get_db),
#     ) -> User:
#         user = await get_current_user(db, credentials.credentials)
#         if user.role != role:
#             raise ForbiddenException(
#                 detail=f"Access denied. Required role: {role.value}"
#             )
#         return user
    
#     return role_checker


def require_roles(roles: list[UserRole]) -> Callable:
    async def roles_checker(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        user = await get_current_user(db, credentials.credentials)
        if user.role not in roles:
            allowed = ", ".join([r.value for r in roles])
            raise ForbiddenException(
                detail=f"Access denied. Required roles: {allowed}"
            )
        return user
    
    return roles_checker


# def require_approver() -> Callable:
#     return require_role(UserRole.APPROVER)


# def require_verifier_or_above() -> Callable:
#     return require_roles([UserRole.VERIFIER, UserRole.APPROVER])
