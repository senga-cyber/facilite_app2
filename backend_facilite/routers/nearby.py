# backend_facilite/routers/nearby.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from geopy.distance import geodesic
from typing import List, Dict, Any, Optional
from backend_facilite.database import get_db
from backend_facilite.models import  Restaurant, Hotel

router = APIRouter(prefix="/nearby", tags=["Nearby"])

@router.get("/", summary="Lister les restaurants et hôtels proches avec note")
def get_nearby_places(
    latitude: float = Query(..., description="Latitude de l'utilisateur"),
    longitude: float = Query(..., description="Longitude de l'utilisateur"),
    radius_km: float = Query(5.0, description="Rayon de recherche en kilomètres"),
    type: Optional[str] = Query(None, description="Filtrer par type: restaurant ou hotel"),
    db: Session = Depends(get_db)
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Retourne les restaurants et hôtels proches avec leurs notes (rating).
    """

    user_location = (latitude, longitude)
    results = []

    # Restaurants
    if type is None or type.lower() == "restaurant":
        restaurants = db.query(Restaurant).all()
        for r in restaurants:
            if r.latitude and r.longitude:
                dist = geodesic(user_location, (r.latitude, r.longitude)).km
                if dist <= radius_km:
                    results.append({
                        "type": "restaurant",
                        "id": r.id,
                        "name": r.name,
                        "address": r.address,
                        "rating": round(r.rating or 0, 1),  # ⭐ note moyenne
                        "distance_km": round(dist, 2),
                        "latitude": r.latitude,
                        "longitude": r.longitude,
                    })

    # Hotels
    if type is None or type.lower() == "hotel":
        hotels = db.query(Hotel).all()
        for h in hotels:
            if h.latitude and h.longitude:
                dist = geodesic(user_location, (h.latitude, h.longitude)).km
                if dist <= radius_km:
                    results.append({
                        "type": "hotel",
                        "id": h.id,
                        "name": h.name,
                        "address": h.address,
                        "rating": round(h.rating or 0, 1),  # ⭐ note moyenne
                        "distance_km": round(dist, 2),
                        "latitude": h.latitude,
                        "longitude": h.longitude,
                    })

    # Trier par distance (croissant)
    results.sort(key=lambda x: x["distance_km"])

    return {"nearby": results}
