from fastapi import Depends, FastAPI, Header, HTTPException

from .database import SessionLocal, init_db
from .repository import RoleRepository, UserRepository
from application.services.role_service import CreateRoleService
from .schemas import CreateRoleRequest, CreateRoleResponse, CreateUserRequest, CreateUserResponse
from application.services.user_service import CreateUserService
from .settings import Settings

app = FastAPI(title="Users API")
init_db()


def require_token(authorization: str | None = Header(default=None)) -> None:
    expected_token = Settings.API_TOKEN
    if expected_token and authorization != f"Bearer {expected_token}":
        raise HTTPException(status_code=401, detail="invalid or missing token")


@app.post("/v1/roles", response_model=CreateRoleResponse, status_code=201)
def create_role(payload: CreateRoleRequest, _: None = Depends(require_token)):
    with SessionLocal() as session:
        service = CreateRoleService(RoleRepository(session=session))
        response = service.execute(payload)
        return response


@app.post("/v1/users", response_model=CreateUserResponse, status_code=201)
def create_user(payload: CreateUserRequest, _: None = Depends(require_token)):
    with SessionLocal() as session:
        service = CreateUserService(UserRepository(session=session))
        response = service.execute(payload)
        return response

