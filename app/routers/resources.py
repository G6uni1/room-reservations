from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.resource import Resource
from app.models.reservation import Reservation, StatusEnum
from app.schemas.resource import ResourceCreate, ResourceUpdate, ResourceOut, AvailabilityOut

router = APIRouter(prefix="/resources", tags=["resources"])


@router.post("/", response_model=ResourceOut, status_code=status.HTTP_201_CREATED)
def create_resource(
    resource_in: ResourceCreate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    resource = Resource(**resource_in.model_dump())
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


@router.get("/", response_model=list[ResourceOut])
def list_resources(db: Session = Depends(get_db)):
    return db.query(Resource).all()


@router.get("/{resource_id}", response_model=ResourceOut)
def get_resource(resource_id: int, db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Recurso não encontrado")
    return resource


@router.put("/{resource_id}", response_model=ResourceOut)
def update_resource(
    resource_id: int,
    resource_in: ResourceUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Recurso não encontrado")

    for field, value in resource_in.model_dump(exclude_unset=True).items():
        setattr(resource, field, value)

    db.commit()
    db.refresh(resource)
    return resource


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Recurso não encontrado")

    db.delete(resource)
    db.commit()


@router.get("/{resource_id}/availability", response_model=AvailabilityOut)
def check_availability(
    resource_id: int,
    inicio: datetime,
    fim: datetime,
    db: Session = Depends(get_db),
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Recurso não encontrado")

    if inicio >= fim:
        raise HTTPException(status_code=400, detail="Data de início deve ser anterior à data de fim")

    conflito = (
        db.query(Reservation)
        .filter(
            Reservation.resource_id == resource_id,
            Reservation.status == StatusEnum.confirmada,
            and_(Reservation.data_inicio < fim, Reservation.data_fim > inicio),
        )
        .first()
    )

    return AvailabilityOut(resource_id=resource_id, disponivel=conflito is None)