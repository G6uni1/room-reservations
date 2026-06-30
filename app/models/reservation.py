import enum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base

class StatusEnum(str, enum.Enum):
    confirmada = "confirmada"
    cancelada = "cancelada"

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    data_inicio = Column(DateTime(timezone=True), nullable=False)
    data_fim = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.confirmada, nullable=False)

    user = relationship("User", back_populates="reservations")
    resource = relationship("Resource", back_populates="reservations")