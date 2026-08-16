from fastapi import Header, HTTPException

from .settings import Settings


def require_token(authorization: str | None = Header(default=None)) -> None:
    expected_token = Settings.API_TOKEN
    if expected_token and authorization != f"Bearer {expected_token}":
        raise HTTPException(status_code=401, detail="invalid or missing token")
