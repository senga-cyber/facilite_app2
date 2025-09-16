# backend_facilite/routers/orders.py 
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from config import get_db, get_current_user
from models import Order, OrderItem, Menu, Restaurant
from schemas import OrderCreate, OrderResponse
from typing import List
import math

router = APIRouter(prefix="/orders", tags=["Orders"])


# -----------------------
# Haversine (calcul distance en km)
# -----------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # rayon de la Terre en km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


# -----------------------
# Commandes à proximité
# -----------------------
@router.get("/nearby/{restaurant_id}", response_model=List[OrderResponse])
def get_nearby_orders(
    restaurant_id: int,
    db: Session = Depends(get_db),
    radius: float = Query(5.0, description="Rayon en km")
):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant introuvable")

    orders = db.query(Order).filter(Order.restaurant_id == restaurant_id).all()
    nearby_orders = []

    for order in orders:
        if order.latitude and order.longitude and restaurant.latitude and restaurant.longitude:
            distance = haversine(
                order.latitude, order.longitude,
                restaurant.latitude, restaurant.longitude
            )
            if distance <= radius:
                nearby_orders.append(order)

    return nearby_orders


# -----------------------
# Voir mes commandes
# -----------------------
@router.get("/me", response_model=List[OrderResponse])
def get_my_orders(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Order).filter(Order.user_id == user.id).all()


# -----------------------
# Voir toutes les commandes (admin)
# -----------------------
@router.get("/", response_model=List[OrderResponse])
def get_all_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


# -----------------------
# Mise à jour position commande
# -----------------------
@router.post("/{order_id}/update-location")
def update_order_location(
    order_id: int,
    lat: float,
    lon: float,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable ou non autorisée")

    order.latitude = lat
    order.longitude = lon
    db.commit()
    db.refresh(order)
    return {"status": "ok", "order_id": order.id, "latitude": lat, "longitude": lon}


# -----------------------
# Suivi commande (client + resto)
# -----------------------
@router.get("/{order_id}/track")
def track_order(order_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable")

    restaurant = db.query(Restaurant).filter(Restaurant.id == order.restaurant_id).first()
    return {
        "order_id": order.id,
        "client_lat": order.latitude,
        "client_lon": order.longitude,
        "restaurant_lat": restaurant.latitude if restaurant else None,
        "restaurant_lon": restaurant.longitude if restaurant else None
    }
