from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ResourceCreate(BaseModel):
    nome: str
    capacidade: int = Field(gt=0)
    descricao: str | None = None


class ResourceUpdate(BaseModel):
    nome: str | None = None
    capacidade: int | None = Field(default=None, gt=0)
    descricao: str | None = None


class ResourceOut(BaseModel):
    id: int
    nome: str
    capacidade: int
    descricao: str | None

    model_config = ConfigDict(from_attributes=True)


class AvailabilityOut(BaseModel):
    resource_id: int
    disponivel: bool