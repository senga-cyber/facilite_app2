# backend_facilite/routers/deliveries.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend_facilite.config import get_db
from backend_facilite.auth import get_current_user
from backend_facilite.models import Delivery, Order, User, RoleEnum, DeliveryStatusEnum
from backend_facilite.schemas import DeliveryCreate, DeliveryUpdate, DeliveryOut

router = APIRouter(prefix="/deliveries", tags=["Deliveries"])


# -----------------------
# Helpers
# -----------------------
def has_role(user: User, role: str) -> bool:
    """Vérifie si un utilisateur possède un rôle donné."""
    if isinstance(user.role, RoleEnum):
        return user.role.value == role
    return str(user.role) == role


def require_roles(user: User, roles: list[str]):
    """Bloque l’accès si l’utilisateur n’a pas l’un des rôles requis."""
    if not any(has_role(user, r) for r in roles):
        raise HTTPException(status_code=403, detail="Accès interdit")


# -----------------------
# 1. Assignation d'une livraison (admin + restaurant_manager)
# -----------------------
@router.post("/", response_model=DeliveryOut)
def assign_delivery(
    payload: DeliveryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_roles(current_user, ["admin", "restaurant_manager"])

    order = db.query(Order).filter(Order.id == payload.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable")

    # Vérifier que la commande n’est pas annulée ou déjà terminée
    if getattr(order, "status", None) in ["cancelled", "completed"]:
        raise HTTPException(status_code=400, detail="Impossible d’assigner une livraison à cette commande")

    # Si restaurant_manager → vérifier que la commande appartient à son resto
    if has_role(current_user, "restaurant_manager"):
        if order.restaurant.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Vous ne pouvez assigner que les commandes de vos restaurants")

    delivery_person = db.query(User).filter(User.id == payload.delivery_person_id).first()
    if not delivery_person:
        raise HTTPException(status_code=404, detail="Livreur introuvable")
    if not has_role(delivery_person, "delivery_person"):
        raise HTTPException(status_code=400, detail="L'utilisateur choisi n'a pas le rôle 'delivery_person'")

    # Vérifier qu’il n’existe pas déjà une livraison pour cette commande
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
# 2. Le livreur voit ses livraisons
# -----------------------
@router.get("/me", response_model=List[DeliveryOut])
def my_deliveries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_roles(current_user, ["delivery_person", "admin"])
    if has_role(current_user, "admin"):
        return db.query(Delivery).all()
    return db.query(Delivery).filter(Delivery.delivery_person_id == current_user.id).all()


# -----------------------
# 3. Suivi d’une commande (client ou admin/manager)
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

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable")

    is_admin = has_role(current_user, "admin")
    is_restomanager = has_role(current_user, "restaurant_manager")
    is_client = (order.user_id == current_user.id)

    if not (is_admin or is_client or (is_restomanager and order.restaurant.owner_id == current_user.id)):
        raise HTTPException(status_code=403, detail="Accès interdit")

    return d


# -----------------------
# 4. Mise à jour (livreur ou admin)
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

    is_admin = has_role(current_user, "admin")
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
# 5. Détail d’une livraison (admin, livreur, client de la commande)
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
    is_admin = has_role(current_user, "admin")
    is_restomanager = has_role(current_user, "restaurant_manager")
    is_delivery = (d.delivery_person_id == current_user.id)
    is_client = (order and order.user_id == current_user.id)

    if not (is_admin or is_delivery or is_client or (is_restomanager and order.restaurant.owner_id == current_user.id)):
        raise HTTPException(status_code=403, detail="Accès interdit")

    return d


# -----------------------
# 6. Suppression d’une livraison (admin uniquement)
# -----------------------
@router.delete("/{delivery_id}", status_code=204)
def delete_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_roles(current_user, ["admin"])
    d = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Livraison introuvable")
    db.delete(d)
    db.commit()
    return
