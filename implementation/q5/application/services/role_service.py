from application.repository import RoleRepository
from application.schemas import CreateRoleRequest, CreateRoleResponse


class CreateRoleService:
    def __init__(self, repository: RoleRepository) -> None:
        self._repository = repository

    def execute(self, request: CreateRoleRequest) -> CreateRoleResponse:
        role = self._repository.create(description=request.description)
        return CreateRoleResponse(id=role.id, description=role.description)
