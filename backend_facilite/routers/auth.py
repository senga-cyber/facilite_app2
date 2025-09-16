from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from config import get_db
from models import User
from schemas import UserCreate, UserResponse, ClientLogin, ManagerLogin

router = APIRouter(prefix="/auth", tags=["Auth"])

# ==========================
# PASSWORD UTILS
# ==========================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ==========================
# JWT CONFIG
# ==========================
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
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé à l’admin")
    return user

# ==========================
# REGISTER CLIENT
# ==========================
@router.post("/register/client", response_model=UserResponse)
def register_client(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.phone == payload.phone).first():
        raise HTTPException(status_code=400, detail="Numéro déjà utilisé")

    hashed_pw = hash_password(payload.password)
    user = User(
        username=payload.username,
        phone=payload.phone,
        email=payload.email,
        password=hashed_pw,
        role="client"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# ==========================
# REGISTER MANAGER (ADMIN ONLY)
# ==========================
@router.post("/register/manager", response_model=UserResponse)
def register_manager(payload: UserCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    if payload.role not in ["restaurant_manager", "hotel_manager"]:
        raise HTTPException(status_code=400, detail="Rôle invalide pour manager")

    if db.query(User).filter(User.phone == payload.phone).first():
        raise HTTPException(status_code=400, detail="Numéro déjà utilisé")

    hashed_pw = hash_password(payload.password)
    user = User(
        username=payload.username,
        phone=payload.phone,
        email=payload.email,
        password=hashed_pw,
        role=payload.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# ==========================
# LOGIN CLIENT (NO PASSWORD)
# ==========================
@router.post("/login/client")
def login_client(payload: ClientLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == payload.phone, User.role == "client").first()
    if not user:
        raise HTTPException(status_code=401, detail="Numéro non reconnu comme client")

    token = create_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

# ==========================
# LOGIN MANAGER & ADMIN
# ==========================
@router.post("/login/manager")
def login_manager(payload: ManagerLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == payload.phone).first()
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")

    if not user.password or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    if user.role not in ["restaurant_manager", "hotel_manager", "admin"]:
        raise HTTPException(status_code=403, detail="Ce rôle ne peut pas se connecter ici")

    token = create_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}
