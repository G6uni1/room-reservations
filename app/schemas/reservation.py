from datetime import datetime
from pydantic import BaseModel, field_validator, ConfigDict
from app.models.reservation import StatusEnum


class ReservationCreate(BaseModel):
    resource_id: int
    data_inicio: datetime
    data_fim: datetime

    @field_validator("data_fim")
    @classmethod
    def fim_apos_inicio(cls, v, info):
        inicio = info.data.get("data_inicio")
        if inicio and v <= inicio:
            raise ValueError("data_fim deve ser posterior a data_inicio")
        return v


class ReservationOut(BaseModel):
    id: int
    user_id: int
    resource_id: int
    data_inicio: datetime
    data_fim: datetime
    status: StatusEnum

    model_config = ConfigDict(from_attributes=True)