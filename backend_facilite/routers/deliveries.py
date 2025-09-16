# backend_facilite/routers/deliveries.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from config import get_db, get_current_user
from models import Delivery, Order, User, RoleEnum, DeliveryStatusEnum
from schemas import DeliveryCreate, DeliveryUpdate, DeliveryOut

router = APIRouter(prefix="/deliveries", tags=["Deliveries"])

def _require_roles(user: User, roles: list[str]):
    if str(user.role) not in roles and user.role not in roles:  # robust check
        # user.role can be RoleEnum or str depending on ORM session
        if (isinstance(user.role, RoleEnum) and user.role.value not in roles):
            raise HTTPException(status_code=403, detail="Accès interdit")
        if (isinstance(user.role, str) and user.role not in roles):
            raise HTTPException(status_code=403, detail="Accès interdit")

# -----------------------
# Assignation d'une livraison (admin + restaurant_manager)
# -----------------------
@router.post("/", response_model=DeliveryOut)
def assign_delivery(
    payload: DeliveryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_roles(current_user, ["admin", "restaurant_manager"])

    order = db.query(Order).filter(Order.id == payload.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable")

    # Si restaurant_manager, vérifier que la commande appartient à un de ses restos
    if str(current_user.role) == "restaurant_manager" or current_user.role == RoleEnum.restaurant_manager:
        if order.restaurant.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Vous ne pouvez assigner que les commandes de vos restaurants")

    delivery_person = db.query(User).filter(User.id == payload.delivery_person_id).first()
    if not delivery_person:
        raise HTTPException(status_code=404, detail="Livreur introuvable")
    if str(delivery_person.role) != "delivery_person" and delivery_person.role != RoleEnum.delivery_person:
        raise HTTPException(status_code=400, detail="L'utilisateur choisi n'a pas le rôle 'delivery_person'")

    # 1 commande → 1 livraison unique
    existing = db.query(Delivery).filter(Delivery.order_id == order.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Une livraison est déjà assignée à cette commande")

    d = Delivery(
        order_id=order.id,
        delivery_person_id=delivery_person.id,
        status=payload.status or DeliveryStatusEnum.pending,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return d

# -----------------------
# Le livreur voit ses livraisons
# -----------------------
@router.get("/me", response_model=List[DeliveryOut])
def my_deliveries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_roles(current_user, ["delivery_person", "admin"])
    if str(current_user.role) == "admin" or current_user.role == RoleEnum.admin:
        # admin peut tout voir
        return db.query(Delivery).all()
    return db.query(Delivery).filter(Delivery.delivery_person_id == current_user.id).all()

# -----------------------
# Suivi d’une commande (client ou admin/manager)
# -----------------------
@router.get("/order/{order_id}", response_model=DeliveryOut)
def get_by_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    d = db.query(Delivery).filter(Delivery.order_id == order_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Livraison introuvable pour cette commande")

    # Autorisations simples :
    # - admin
    # - restaurant_manager du resto concerné
    # - client qui a passé la commande
    order = db.query(Order).filter(Order.id == order_id).first()
    is_admin = (str(current_user.role) == "admin" or current_user.role == RoleEnum.admin)
    is_restomanager = (str(current_user.role) == "restaurant_manager" or current_user.role == RoleEnum.restaurant_manager)
    is_client = (order and order.user_id == current_user.id)

    if not (is_admin or is_client or (is_restomanager and order.restaurant.owner_id == current_user.id)):
        raise HTTPException(status_code=403, detail="Accès interdit")

    return d

# -----------------------
# Mise à jour (livreur ou admin)
# -----------------------
@router.patch("/{delivery_id}", response_model=DeliveryOut)
def update_delivery(
    delivery_id: int,
    payload: DeliveryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    d = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Livraison introuvable")

    is_admin = (str(current_user.role) == "admin" or current_user.role == RoleEnum.admin)
    is_owner = (d.delivery_person_id == current_user.id)

    if not (is_admin or is_owner):
        raise HTTPException(status_code=403, detail="Seul l'admin ou le livreur assigné peut modifier la livraison")

    if payload.status is not None:
        d.status = payload.status
    if payload.latitude is not None:
        d.latitude = payload.latitude
    if payload.longitude is not None:
        d.longitude = payload.longitude

    db.commit()
    db.refresh(d)
    return d

# -----------------------
# Détail d’une livraison (admin, livreur, client de la commande)
# -----------------------
@router.get("/{delivery_id}", response_model=DeliveryOut)
def get_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    d = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Livraison introuvable")

    order = db.query(Order).filter(Order.id == d.order_id).first()
    is_admin = (str(current_user.role) == "admin" or current_user.role == RoleEnum.admin)
    is_restomanager = (str(current_user.role) == "restaurant_manager" or current_user.role == RoleEnum.restaurant_manager)
    is_delivery = (d.delivery_person_id == current_user.id)
    is_client = (order and order.user_id == current_user.id)

    if not (is_admin or is_delivery or is_client or (is_restomanager and order.restaurant.owner_id == current_user.id)):
        raise HTTPException(status_code=403, detail="Accès interdit")

    return d
