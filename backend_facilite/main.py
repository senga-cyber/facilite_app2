# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text 
from config import get_db  
from database import Base, engine
from routers import users, hotels, reservations, restaurants, orders, payments, deliveries 
from auth import router as auth_router  # Ajout du routeur auth
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware




app = FastAPI(title="facilte_app2")
# main.py


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Servir les QR codes
app.mount("/static", StaticFiles(directory="static"), name="static")

# Création des tables dans PostgreSQL
Base.metadata.create_all(bind=engine)



# Inclusion des routes
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(hotels.router, prefix="/hotels", tags=["Hotels"])
app.include_router(reservations.router, prefix="/reservations", tags=["Reservations"])
app.include_router(restaurants.router, prefix="/restaurants", tags=["Restaurants"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(payments.router)
app.include_router(auth_router)  # Inclusion du routeur auth
app.include_router(deliveries.router)  # ✅ Inclusion du routeur deliveries

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'application"}

@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1")).fetchone()
    return {"success": True, "value": result[0]}
