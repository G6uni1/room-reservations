from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.user import RoleEnum


class UserCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str


class UserLogin(BaseModel):
    email: EmailStr
    senha: str


class UserOut(BaseModel):
    id: int
    nome: str
    email: EmailStr
    role: RoleEnum

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"