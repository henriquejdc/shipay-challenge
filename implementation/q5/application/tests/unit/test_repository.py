from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from application.database import Base
from application.models import Role
from application.repository import RoleRepository, UserRepository


def test_role_repository_creates_role():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        repository = RoleRepository(session=session)
        role = repository.create(description="admin")

        assert role.id is not None
        assert role.description == "admin"
        assert repository.exists(role.id) is True
        assert repository.exists(999) is False


def test_user_repository_creates_user_and_checks_email():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        session.add(Role(id=1, description="admin"))
        session.commit()

        repository = UserRepository(session=session)
        assert repository.role_exists(1) is True
        assert repository.exists_by_email("user@example.com") is False

        user = repository.create(
            name="User",
            email="user@example.com",
            hashed_password="hash",
            role_id=1,
        )

        assert user.id is not None
        assert user.created_at == date.today()
        assert repository.exists_by_email("user@example.com") is True

