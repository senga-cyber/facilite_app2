# routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config import get_db
from models import User
from schemas import UserCreate, UserReponse
from typing import List
from auth import hash_password

router = APIRouter(tags=["Users"])  # <-- pas besoin de prefix ici, car déjà défini dans main.py

@router.post("/", response_model=UserReponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Vérifier si le numéro ou l'email existe déjà
    db_user = db.query(User).filter(
        (User.phone_number == user.phone_number) | (User.name == user.name)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Utilisateur déjà existant")

    # Créer un nouvel utilisateur
    new_user = User(
        name=user.name,
        phone_number=user.phone_number,
        hashed_password=hash_password(user.password) if user.password else None,
        role=user.role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
