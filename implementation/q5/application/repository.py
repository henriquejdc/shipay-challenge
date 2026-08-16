from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Role, User


class RoleRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, *, description: str) -> Role:
        role = Role(description=description)
        self._session.add(role)
        self._session.commit()
        self._session.refresh(role)
        return role

    def exists(self, role_id: int) -> bool:
        stmt = select(Role.id).where(Role.id == role_id)
        return self._session.execute(stmt).scalar_one_or_none() is not None


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def exists_by_email(self, email: str) -> bool:
        stmt = select(User.id).where(User.email == email)
        return self._session.execute(stmt).scalar_one_or_none() is not None

    def role_exists(self, role_id: int) -> bool:
        stmt = select(Role.id).where(Role.id == role_id)
        return self._session.execute(stmt).scalar_one_or_none() is not None

    def create(self, *, name: str, email: str, hashed_password: str, role_id: int) -> User:
        user = User(
            name=name,
            email=email,
            password=hashed_password,
            role_id=role_id,
            created_at=date.today(),
            updated_at=None,
        )
        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        return user

