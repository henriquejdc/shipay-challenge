from pydantic import BaseModel, EmailStr, Field


class CreateRoleRequest(BaseModel):
    description: str = Field(min_length=2, max_length=120)


class CreateRoleResponse(BaseModel):
    id: int
    description: str


class CreateUserRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    role_id: int
    password: str | None = Field(default=None, min_length=8, max_length=128)


class CreateUserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role_id: int
    auto_generated_password: bool


