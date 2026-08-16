from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from application.database import Base
from application.repository import RoleRepository
from application.services.role_service import CreateRoleService
from application.schemas import CreateRoleRequest


def test_create_role_service_creates_role():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        repository = RoleRepository(session=session)
        service = CreateRoleService(repository=repository)

        request = CreateRoleRequest(description="admin")
        response = service.execute(request)

        assert response.id is not None
        assert response.description == "admin"
