from collections.abc import Generator

from fastapi import Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_auth(x_api_key: str = Header(...)) -> None:
    if not verify_api_key(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
