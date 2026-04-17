from fastapi import HTTPException, status
from services.crypto_assets.security import CurrentUser

FULL_ACCESS_ROLES = {"FINANCE_DIRECTOR", "HEAD_OF_PAYMENTS"}
READ_ONLY_ROLES = {"OPERATIONS"}


def require_write_access(user: CurrentUser) -> None:
    if user.role in READ_ONLY_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="OPERATIONS role has read-only access",
        )
