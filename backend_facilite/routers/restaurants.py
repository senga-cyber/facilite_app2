from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend_facilite.config import get_db
from backend_facilite.auth import get_current_user

from backend_facilite.models import Restaurant, Menu, User
from backend_facilite.schemas import RestaurantCreate, RestaurantResponse, MenuCreate, MenuResponse
from typing import List

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


# ✅ Créer un restaurant (admin uniquement)
@router.post("/", response_model=RestaurantResponse)
def create_restaurant(
    restaurant: RestaurantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Seul un admin peut créer un restaurant")

    manager = db.query(User).filter(
        User.id == restaurant.manager_id,
        User.role == "restaurant_manager"
    ).first()

    if not manager:
        raise HTTPException(status_code=404, detail="Manager introuvable ou rôle invalide")

    db_restaurant = Restaurant(
        name=restaurant.name,
        location=restaurant.location,
        description=restaurant.description,
        owner_id=manager.id
    )

    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant


# ✅ Lister tous les restaurants
@router.get("/", response_model=List[RestaurantResponse])
def list_restaurants(db: Session = Depends(get_db)):
    return db.query(Restaurant).all()


# ✅ Ajouter un menu à un restaurant
@router.post("/{restaurant_id}/menu", response_model=MenuResponse)
def add_menu(restaurant_id: int, menu: MenuCreate, db: Session = Depends(get_db)):
    db_restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not db_restaurant:
        raise HTTPException(status_code=404, detail="Restaurant introuvable")

    db_menu = Menu(**menu.dict(), restaurant_id=restaurant_id)
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    return db_menu


# ✅ Lister les menus d’un restaurant
@router.get("/{restaurant_id}/menu", response_model=List[MenuResponse])
def list_menu(restaurant_id: int, db: Session = Depends(get_db)):
    return db.query(Menu).filter(Menu.restaurant_id == restaurant_id).all()
