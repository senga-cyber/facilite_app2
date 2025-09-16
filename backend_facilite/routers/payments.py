from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config import get_db, get_current_user
from models import Payment, Order, Reservation, User
from schemas import PaymentCreate, PaymentOut
from typing import List
from datetime import datetime
from sqlalchemy import func
import os

from utils.qrcode_utils import ensure_tx_code, generate_qr_png

router = APIRouter(prefix="/payments", tags=["Payments"])

# ✅ Modes de paiement supportés
SUPPORTED = ["airtel_money", "orange_money", "mpesa", "visa", "mastercard", "cash"]

# ✅ Calcul des commissions
def compute_commission(amount: float, method: str) -> float:
    app_fee = 2.0   # frais fixe
    gateway = 0.0
    if method in ["visa", "mastercard"]:
        gateway = 0.02 * amount
    elif method in ["airtel_money", "orange_money", "mpesa"]:
        gateway = 0.01 * amount
    return app_fee + gateway

# ✅ Créer un paiement avec génération QR Code#

@router.post("/", response_model=PaymentOut)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not payment.order_id and not payment.reservation_id:
        raise HTTPException(status_code=400, detail="Un paiement doit être lié à une commande ou une réservation.")

    if payment.payment_method not in SUPPORTED:
        raise HTTPException(status_code=400, detail="Méthode de paiement non supportée")

    # Vérifications
    if payment.order_id and not db.query(Order).filter(Order.id == payment.order_id).first():
        raise HTTPException(status_code=404, detail="Commande introuvable")

    if payment.reservation_id and not db.query(Reservation).filter(Reservation.id == payment.reservation_id).first():
        raise HTTPException(status_code=404, detail="Réservation introuvable")

    commission = compute_commission(payment.amount, payment.payment_method)
    net_amount = payment.amount - commission
    tx_code = ensure_tx_code()

    db_payment = Payment(
        user_id=current_user.id,
        order_id=payment.order_id,
        reservation_id=payment.reservation_id,
        amount=payment.amount,
        net_amount=net_amount,
        commission=commission,
        payment_method=payment.payment_method,
        status="success",
        transaction_code=tx_code,
        is_used=False,
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    # ✅ Génération du QR
    qr_payload = {
        "transaction_code": tx_code,
        "user_id": current_user.id,
        "order_id": payment.order_id,
        "reservation_id": payment.reservation_id,
        "ts": int(datetime.utcnow().timestamp()),
    }
    qr_filename = f"{tx_code}.png"
    qr_path = os.path.join("static/qrcodes", qr_filename)
    generate_qr_png(qr_payload, qr_path)

    db_payment.qr_path = qr_path
    db.commit()
    db.refresh(db_payment)

    # ✅ Retour URL publique
    qr_url = f"/static/qrcodes/{qr_filename}"

    return {
        **db_payment.__dict__,
        "qr_url": qr_url
    }


# ✅ Lister mes paiements
@router.get("/me", response_model=List[PaymentOut])
def get_my_payments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Payment).filter(Payment.user_id == current_user.id).all()


# ✅ Lister tous les paiements (admin uniquement)
@router.get("/", response_model=List[PaymentOut])
def list_payments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé à l’admin")
    return db.query(Payment).all()


# ✅ Récupérer un paiement par ID
@router.get("/{payment_id}", response_model=PaymentOut)
def get_payment(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pay = db.query(Payment).filter(Payment.id == payment_id).first()
    if not pay:
        raise HTTPException(status_code=404, detail="Paiement introuvable")
    if current_user.role != "admin" and pay.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Non autorisé")
    return pay


# ✅ Validation (scan du QR côté staff)
from pydantic import BaseModel

class QRValidateIn(BaseModel):
    transaction_code: str

@router.post("/validate")
def validate_qr(
    body: QRValidateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["admin", "restaurant_manager", "hotel_manager"]:
        raise HTTPException(status_code=403, detail="Réservé au staff (admin/manager)")

    pay = db.query(Payment).filter(Payment.transaction_code == body.transaction_code).first()
    if not pay:
        raise HTTPException(status_code=404, detail="Transaction inconnue")

    if pay.is_used:
        raise HTTPException(status_code=400, detail="QR déjà validé / utilisé")

    pay.is_used = True
    db.commit()

    if pay.qr_path and os.path.exists(pay.qr_path):
        try:
            os.remove(pay.qr_path)
            pay.qr_path = None
            db.commit()
        except Exception:
            pass

    return {"status": "ok", "message": "QR validé, accès autorisé", "payment_id": pay.id}


# ✅ Statistiques mensuelles des commissions (admin)
@router.get("/commissions/stats")
def get_commission_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")

    results = (
        db.query(
            func.date_trunc('month', Payment.created_at).label("mois"),
            func.sum(Payment.commission).label("total_commission"),
            func.count(Payment.id).label("nb_paiements")
        )
        .group_by(func.date_trunc('month', Payment.created_at))
        .order_by(func.date_trunc('month', Payment.created_at))
        .all()
    )

    return [
        {
            "mois": r.mois.strftime("%Y-%m"),
            "total_commission": float(r.total_commission),
            "nb_paiements": r.nb_paiements
        }
        for r in results
    ]


# ✅ Total des commissions (admin)
@router.get("/commissions/total")
def get_total_commissions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")

    total_commission = db.query(func.sum(Payment.commission)).scalar() or 0.0
    total_payments = db.query(func.count(Payment.id)).scalar() or 0

    return {
        "total_commissions": total_commission,
        "nombre_paiements": total_payments
    }
