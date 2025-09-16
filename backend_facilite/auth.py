from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from database import get_db
from models import User, RoleEnum
from schemas import UserBase, ClientLogin, ManagerLogin, UserReponse, UserCreate, ManagerCreate

router = APIRouter(prefix="/auth", tags=["Auth"])

# pour hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWT config
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()

def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        role = payload.get("role")
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
# Inscription client
# ======================
@router.post("/register/client", response_model=UserReponse)
def register_client(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.phone_number == payload.phone_number).first():
        raise HTTPException(status_code=400, detail="Numéro déjà utilisé")

    user = User(name=payload.name, phone_number=payload.phone_number, role="client")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# ======================
# Inscription manager (protégée, admin uniquement)
# ======================
@router.post("/register/manager", response_model=UserReponse)
def register_manager(payload: ManagerCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    if payload.role not in [RoleEnum.restaurant_manager, RoleEnum.hotel_manager]:
        raise HTTPException(status_code=400, detail="Role invalide pour manager")

    if db.query(User).filter(User.phone_number == payload.phone_number).first():
        raise HTTPException(status_code=400, detail="Numéro déjà utilisé")

    hashed_pw = pwd_context.hash(payload.password)
    user = User(
        name=payload.name,
        phone_number=payload.phone_number,
        password=hashed_pw,
        role=payload.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ======================
# Connexion client (sans mot de passe)
# ======================
@router.post("/login/client")
def login_client(payload: ClientLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == payload.phone_number, User.role == RoleEnum.client).first()
    if not user:
        raise HTTPException(status_code=401, detail="Numéro non reconnu comme client")

    token = create_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

# ======================
# Connexion manager/admin
# ======================
@router.post("/login/manager")
def login_manager(payload: ManagerLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == payload.phone_number).first()
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")

    if not user.password or not pwd_context.verify(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    if user.role not in [RoleEnum.restaurant_manager, RoleEnum.hotel_manager, RoleEnum.admin]:
        raise HTTPException(status_code=403, detail="Ce rôle ne peut pas se connecter ici")

    token = create_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}
# ======================