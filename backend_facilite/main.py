from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend_facilite.config import get_db
from backend_facilite.database import Base, engine
from backend_facilite.routers import (
    users, hotels, reservations, restaurants,
    orders, payments, deliveries, location, nearby
)
from backend_facilite.auth import router as auth_router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="facilte_app2")

# ==========================
# Middleware CORS
# ==========================
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Autorise uniquement le frontend
    allow_credentials=True,
    allow_methods=["*"],          # GET, POST, PUT, DELETE, OPTIONS
    allow_headers=["*"],          # Tous les headers autorisés
)

# ==========================
# Static files
# ==========================
app.mount("/static", StaticFiles(directory="static"), name="static")

# ==========================
# Création des tables
# ==========================
Base.metadata.create_all(bind=engine)

# ==========================
# Routes incluses
# ==========================
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(hotels.router, prefix="/hotels", tags=["Hotels"])
app.include_router(reservations.router, prefix="/reservations", tags=["Reservations"])
app.include_router(restaurants.router, prefix="/restaurants", tags=["Restaurants"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(payments.router, tags=["Payments"])
app.include_router(auth_router)
app.include_router(deliveries.router, prefix="/deliveries", tags=["Deliveries"])
app.include_router(location.router, prefix="/location", tags=["Location"])
app.include_router(nearby.router, prefix="/nearby", tags=["Nearby"])


# ==========================
# Endpoints de test
# ==========================
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur facility, la plateforme qui vous facilite votre quotidien!"}


@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1")).fetchone()
    return {"success": True, "value": result[0]}
