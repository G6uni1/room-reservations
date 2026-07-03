from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.models.resource import Resource
from app.models.reservation import Reservation, StatusEnum
from app.models.user import User
from app.schemas.reservation import ReservationCreate, ReservationOut

router = APIRouter(prefix="/reservations", tags=["reservations"])


def _has_conflict(db: Session, resource_id: int, inicio, fim, exclude_id: int | None = None) -> bool:
    query = db.query(Reservation).filter(
        Reservation.resource_id == resource_id,
        Reservation.status == StatusEnum.confirmada,
        and_(Reservation.data_inicio < fim, Reservation.data_fim > inicio),
    )
    if exclude_id:
        query = query.filter(Reservation.id != exclude_id)
    return query.first() is not None


@router.post("/", response_model=ReservationOut, status_code=status.HTTP_201_CREATED)
def create_reservation(
    reservation_in: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resource = db.query(Resource).filter(Resource.id == reservation_in.resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Recurso não encontrado")

    if _has_conflict(db, reservation_in.resource_id, reservation_in.data_inicio, reservation_in.data_fim):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma reserva confirmada nesse intervalo de horário",
        )

    reservation = Reservation(
        user_id=current_user.id,
        resource_id=reservation_in.resource_id,
        data_inicio=reservation_in.data_inicio,
        data_fim=reservation_in.data_fim,
        status=StatusEnum.confirmada,
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


@router.get("/me", response_model=list[ReservationOut])
def list_my_reservations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Reservation).filter(Reservation.user_id == current_user.id).all()


@router.get("/", response_model=list[ReservationOut])
def list_all_reservations(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    return db.query(Reservation).all()


@router.patch("/{reservation_id}/cancel", response_model=ReservationOut)
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")

    if reservation.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Você não pode cancelar reserva de outro usuário")

    if reservation.status == StatusEnum.cancelada:
        raise HTTPException(status_code=400, detail="Reserva já está cancelada")

    reservation.status = StatusEnum.cancelada
    db.commit()
    db.refresh(reservation)
    return reservation