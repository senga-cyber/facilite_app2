# backend_facilite/routers/location.py
from fastapi import APIRouter, Query
from geopy.distance import geodesic

router = APIRouter(prefix="/location", tags=["Location"])

@router.get("/distance")
def calculate_distance(
    lat1: float = Query(..., description="Latitude du point A (ex: client)"),
    lon1: float = Query(..., description="Longitude du point A (ex: client)"),
    lat2: float = Query(..., description="Latitude du point B (ex: restaurant/hôtel)"),
    lon2: float = Query(..., description="Longitude du point B (ex: restaurant/hôtel)"),
):
    """
    Calcule la distance entre deux points (A et B) en kilomètres.
    """
    pointA = (lat1, lon1)
    pointB = (lat2, lon2)
    distance_km = geodesic(pointA, pointB).km
    return {
        "pointA": {"lat": lat1, "lon": lon1},
        "pointB": {"lat": lat2, "lon": lon2},
        "distance_km": round(distance_km, 2)
    }
