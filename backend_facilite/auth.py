# backend_facilite/auth.py
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

from backend_facilite.database import get_db
from backend_facilite.models import User, RoleEnum, Restaurant, Hotel
from backend_facilite.schemas import (
    UserCreate, ClientLogin, ManagerLogin, ManagerCreate
)

router = APIRouter(prefix="/auth", tags=["Auth"])

# ======================
# CONFIG
# ======================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()

def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    token: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
    return user

def require_admin(user=Depends(get_current_user)):
    if user.role != RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Accès réservé à l’admin")
    return user


# ======================
# ROUTES
# ======================

# --- 1. Inscription client (avec auto-login)
@router.post("/register/client")
def register_client(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.phone_number == payload.phone_number).first():
        raise HTTPException(status_code=400, detail="Numéro déjà utilisé")

    hashed_pw = hash_password(payload.password)

    user = User(
        name=payload.name,
        phone_number=payload.phone_number,
        hashed_password=hashed_pw,
        role=RoleEnum.client
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token({"sub": str(user.id), "role": user.role})

    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "phone_number": user.phone_number,
            "role": user.role,
            "created_at": user.created_at
        },
        "access_token": token,
        "token_type": "bearer"
    }


# --- 2. Inscription manager (admin uniquement, lié à resto/hôtel)
@router.post("/register/manager")
def register_manager(
    payload: ManagerCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    if payload.role not in [RoleEnum.restaurant_manager, RoleEnum.hotel_manager]:
        raise HTTPException(status_code=400, detail="Rôle invalide pour manager")

    if db.query(User).filter(User.phone_number == payload.phone_number).first():
        raise HTTPException(status_code=400, detail="Numéro déjà utilisé")

    hashed_pw = hash_password(payload.password)

    user = User(
        name=payload.name,
        phone_number=payload.phone_number,
        hashed_password=hashed_pw,
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Association directe
    if payload.role == RoleEnum.restaurant_manager and getattr(payload, "restaurant_id", None):
        restaurant = db.query(Restaurant).filter(Restaurant.id == payload.restaurant_id).first()
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant introuvable")
        restaurant.owner_id = user.id
    elif payload.role == RoleEnum.hotel_manager and getattr(payload, "hotel_id", None):
        hotel = db.query(Hotel).filter(Hotel.id == payload.hotel_id).first()
        if not hotel:
            raise HTTPException(status_code=404, detail="Hôtel introuvable")
        hotel.owner_id = user.id
    else:
        raise HTTPException(status_code=400, detail="ID restaurant/hôtel requis pour ce manager")

    db.commit()

    token = create_token({"sub": str(user.id), "role": user.role})

    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "phone_number": user.phone_number,
            "role": user.role,
            "created_at": user.created_at
        },
        "access_token": token,
        "token_type": "bearer"
    }


# --- 3. Connexion client (sans mot de passe)
@router.post("/login/client")
def login_client(payload: ClientLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.phone_number == payload.phone_number,
        User.role == RoleEnum.client
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Numéro non reconnu comme client")

    token = create_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


# --- 4. Connexion manager/admin (avec mot de passe)
@router.post("/login/manager")
def login_manager(payload: ManagerLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == payload.phone_number).first()
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")

    if not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    if user.role not in [RoleEnum.restaurant_manager, RoleEnum.hotel_manager, RoleEnum.admin]:
        raise HTTPException(status_code=403, detail="Ce rôle ne peut pas se connecter ici")

    token = create_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}
