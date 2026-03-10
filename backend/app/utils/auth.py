from typing import Callable
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.services.auth_service import get_current_user
from app.errors import ForbiddenException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def require_auth(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    return await get_current_user(db, token)


# def require_role(role: UserRole) -> Callable:
#     async def role_checker(
#         token: str = Depends(oauth2_scheme),
#         db: AsyncSession = Depends(get_db),
#     ) -> User:
#         user = await get_current_user(db, token)
#         if user.role != role:
#             raise ForbiddenException(
#                 detail=f"Access denied. Required role: {role.value}"
#             )
#         return user
    
#     return role_checker


def require_roles(roles: list[UserRole]) -> Callable:
    async def roles_checker(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        user = await get_current_user(db, token)
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
