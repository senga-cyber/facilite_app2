from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config import get_db, get_current_user
from models import Payment, Order, Reservation, User
from schemas import PaymentCreate, PaymentOut
from typing import List
from datetime import datetime
import os
import qrcode

router = APIRouter(prefix="/payments", tags=["Payments"])

QR_FOLDER = "static/qrcodes"

# ✅ Créer un paiement avec génération QR Code
@router.post("/", response_model=PaymentOut)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not payment.order_id and not payment.reservation_id:
        raise HTTPException(status_code=400, detail="Un paiement doit être lié à une commande ou une réservation.")

    supported_methods = ["airtel_money", "orange_money", "mpesa", "visa", "mastercard", "cash"]
    if payment.payment_method not in supported_methods:
        raise HTTPException(status_code=400, detail="Méthode de paiement non supportée")

    commission = 0.02 * payment.amount if payment.payment_method in ["visa", "mastercard"] else 0.01 * payment.amount
    net_amount = payment.amount - commission

    txn_code = f"TXN-{datetime.utcnow().timestamp()}"

    db_payment = Payment(
        user_id=current_user.id,
        order_id=payment.order_id,
        reservation_id=payment.reservation_id,
        amount=payment.amount,
        net_amount=net_amount,
        commission=commission,
        payment_method=payment.payment_method,
        status="success",
        transaction_code=txn_code
    )

    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    # ✅ Générer QR Code
    qr_data = f"Paiement confirmé - TXN: {txn_code} - Utilisateur: {current_user.phone_number}"
    qr = qrcode.make(qr_data)

    if not os.path.exists(QR_FOLDER):
        os.makedirs(QR_FOLDER)

    qr_filename = f"{txn_code}.png"
    qr_path = os.path.join(QR_FOLDER, qr_filename)
    qr.save(qr_path)

    return {
        **db_payment.__dict__,
        "qr_code": f"{QR_FOLDER}/{qr_filename}"
    }

# ✅ Lister tous les paiements (admin uniquement)
@router.get("/", response_model=List[PaymentOut])
def list_payments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé à l’admin")
    return db.query(Payment).all()

# ✅ Récupérer un paiement par ID
@router.get("/{payment_id}", response_model=PaymentOut)
def get_payment(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Paiement introuvable")
    return payment
