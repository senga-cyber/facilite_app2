from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config import get_db, get_current_user
from models import Hotel, User, Room, Reservation
from schemas import (
    HotelCreate, HotelUpdate, HotelResponse,
    RoomCreate, RoomReponse ,
    ReservationCreate, ReservationOut
)
from typing import List

router = APIRouter(prefix="/hotels", tags=["Hotels"])

# ✅ Ajouter un hôtel (admin uniquement)
@router.post("/", response_model=HotelResponse)
def create_hotel(
    hotel: HotelCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Seul un admin peut créer un hôtel")

    manager = db.query(User).filter(
        User.id == hotel.manager_id,
        User.role == "hotel_manager"
    ).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager introuvable ou rôle invalide")

    db_hotel = Hotel(
        name=hotel.name,
        address=hotel.address,
        latitude=hotel.latitude,
        longitude=hotel.longitude,
        owner_id=manager.id
    )
    db.add(db_hotel)
    db.commit()
    db.refresh(db_hotel)
    return db_hotel


# ✅ Récupérer tous les hôtels
@router.get("/", response_model=List[HotelResponse])
def get_hotels(db: Session = Depends(get_db)):
    return db.query(Hotel).all()


# ✅ Récupérer un hôtel par ID
@router.get("/{hotel_id}", response_model=HotelResponse)
def get_hotel(hotel_id: int, db: Session = Depends(get_db)):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hôtel introuvable")
    return hotel


# ✅ Mettre à jour un hôtel
@router.put("/{hotel_id}", response_model=HotelResponse)
def update_hotel(
    hotel_id: int,
    hotel: HotelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not db_hotel:
        raise HTTPException(status_code=404, detail="Hôtel introuvable")

    if current_user.role not in ["admin", "hotel_manager"]:
        raise HTTPException(status_code=403, detail="Seul un admin ou le manager peut modifier cet hôtel")

    for key, value in hotel.dict(exclude_unset=True).items():
        setattr(db_hotel, key, value)

    db.commit()
    db.refresh(db_hotel)
    return db_hotel


# ✅ Supprimer un hôtel
@router.delete("/{hotel_id}")
def delete_hotel(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hôtel introuvable")

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Seul un admin peut supprimer un hôtel")

    db.delete(hotel)
    db.commit()
    return {"message": "Hôtel supprimé avec succès"}


# -----------------------
# ✅ ROOMS (CHAMBRES)
# -----------------------
@router.post("/{hotel_id}/rooms", response_model=RoomReponse)
def add_room(
    hotel_id: int,
    room: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hôtel introuvable")

    if current_user.role not in ["admin", "hotel_manager"]:
        raise HTTPException(status_code=403, detail="Seul un admin ou le manager peut ajouter des chambres")

    db_room = Room(
        hotel_id=hotel_id,
        room_number=room.room_number,
        capacity=room.capacity,
        price_per_night=room.price_per_night
    )
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


@router.get("/{hotel_id}/rooms", response_model=List[RoomReponse])
def list_rooms(hotel_id: int, db: Session = Depends(get_db)):
    return db.query(Room).filter(Room.hotel_id == hotel_id).all()


# -----------------------
# ✅ RESERVATIONS
# -----------------------
@router.post("/{hotel_id}/reservations", response_model=ReservationOut)
def create_reservation(
    hotel_id: int,
    reservation: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hôtel introuvable")

    # Calcul du prix total (nombre de nuits * prix par nuit)
    nights = (reservation.check_out - reservation.check_in).days
    if nights <= 0:
        raise HTTPException(status_code=400, detail="La date de sortie doit être après la date d'entrée")

    total_price = nights * hotel.price_per_night

    db_reservation = Reservation(
        user_id=current_user.id,
        hotel_id=hotel_id,
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


@router.get("/{hotel_id}/reservations", response_model=List[ReservationOut])
def list_reservations(hotel_id: int, db: Session = Depends(get_db)):
    return db.query(Reservation).filter(Reservation.hotel_id == hotel_id).all()
