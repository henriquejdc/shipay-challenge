from fastapi import HTTPException

from application.services.password_service import PasswordService
from application.repository import UserRepository
from application.schemas import CreateUserRequest, CreateUserResponse


class CreateUserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def execute(self, payload: CreateUserRequest) -> CreateUserResponse:
        if self._repository.exists_by_email(payload.email):
            raise HTTPException(status_code=409, detail="email already registered")

        if not self._repository.role_exists(payload.role_id):
            raise HTTPException(status_code=400, detail="invalid role_id")

        password_result = PasswordService.build_password(payload.password)
        user = self._repository.create(
            name=payload.name,
            email=payload.email,
            hashed_password=password_result.hashed_password,
            role_id=payload.role_id,
        )

        return CreateUserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role_id=user.role_id,
            auto_generated_password=password_result.auto_generated,
        )

