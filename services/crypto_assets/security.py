from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status


@dataclass
class CurrentUser:
    username: str
    role: str


ROLE_TOKENS = {
    "finance-director-token": CurrentUser(username="lidia", role="FINANCE_DIRECTOR"),
    "head-payments-token": CurrentUser(username="sasha", role="HEAD_OF_PAYMENTS"),
    "operations-token": CurrentUser(username="anton", role="OPERATIONS"),
}


def get_current_user(authorization: str | None = Header(default=None)) -> CurrentUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    token = authorization.removeprefix("Bearer ").strip()
    user = ROLE_TOKENS.get(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return user


def require_roles(*allowed_roles: str):
    def checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role",
            )
        return user

    return checker
