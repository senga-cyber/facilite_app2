# backend_facilite/routers/reservations.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config import get_db, get_current_user
from models import Reservation, Hotel
from schemas import ReservationCreate, ReservationOut
from datetime import datetime
from typing import List

router = APIRouter(prefix="/reservations", tags=["Reservations"])


# -----------------------
# Créer une réservation
# -----------------------
@router.post("/", response_model=ReservationOut)
def create_reservation(
    reservation: ReservationCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    hotel = db.query(Hotel).filter(Hotel.id == reservation.hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hôtel introuvable")

    # Calcul du prix total
    nights = (reservation.check_out - reservation.check_in).days
    if nights <= 0:
        raise HTTPException(status_code=400, detail="Les dates sont invalides")

    total_price = nights * hotel.price_per_night

    db_reservation = Reservation(
        user_id=user.id,
        hotel_id=reservation.hotel_id,
        check_in=reservation.check_in,
        check_out=reservation.check_out,
        total_price=total_price,
        latitude=reservation.latitude,
        longitude=reservation.longitude
    )

    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation


# -----------------------
# Voir mes réservations
# -----------------------
@router.get("/me", response_model=List[ReservationOut])
def get_my_reservations(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Reservation).filter(Reservation.user_id == user.id).all()


# -----------------------
# Voir toutes les réservations (admin)
# -----------------------
@router.get("/", response_model=List[ReservationOut])
def get_all_reservations(db: Session = Depends(get_db)):
    return db.query(Reservation).all()


# -----------------------
# Mise à jour position client (réservation)
# -----------------------
@router.post("/{reservation_id}/update-location")
def update_reservation_location(
    reservation_id: int,
    lat: float,
    lon: float,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.user_id == user.id
    ).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation introuvable ou non autorisée")

    reservation.latitude = lat
    reservation.longitude = lon
    db.commit()
    db.refresh(reservation)
    return {
        "status": "ok",
        "reservation_id": reservation.id,
        "latitude": lat,
        "longitude": lon
    }


# -----------------------
# Suivi réservation (client + hôtel)
# -----------------------
@router.get("/{reservation_id}/track")
def track_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation introuvable")

    hotel = db.query(Hotel).filter(Hotel.id == reservation.hotel_id).first()

    return {
        "reservation_id": reservation.id,
        "client_lat": reservation.latitude,
        "client_lon": reservation.longitude,
        "hotel_lat": hotel.latitude if hotel else None,
        "hotel_lon": hotel.longitude if hotel else None
    }
