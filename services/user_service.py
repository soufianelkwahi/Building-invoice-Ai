from sqlalchemy.orm import Session

from app.core.security import hash_api_key
from db.models import User


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, username: str, email: str, api_key: str) -> User:
        user = User(
            username=username,
            email=email,
            hashed_api_key=hash_api_key(api_key),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_api_key(self, api_key: str) -> User | None:
        hashed = hash_api_key(api_key)
        return self.db.query(User).filter(User.hashed_api_key == hashed).first()

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()
