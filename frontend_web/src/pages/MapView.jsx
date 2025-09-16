// frontend_web/src/pages/MapView.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Icônes personnalisées
const clientIcon = new L.Icon({
  iconUrl: "https://cdn-icons-png.flaticon.com/512/4872/4872869.png",
  iconSize: [32, 32],
});

const hotelIcon = new L.Icon({
  iconUrl: "https://cdn-icons-png.flaticon.com/512/888/888064.png",
  iconSize: [32, 32],
});

const restaurantIcon = new L.Icon({
  iconUrl: "https://cdn-icons-png.flaticon.com/512/3075/3075977.png",
  iconSize: [32, 32],
});

export default function MapView() {
  const [hotels, setHotels] = useState([]);
  const [restaurants, setRestaurants] = useState([]);
  const [userPos, setUserPos] = useState(null);

  // Charger hôtels & restaurants depuis API backend
  useEffect(() => {
    (async () => {
      try {
        const h = await axios.get("http://127.0.0.1:8000/hotels/");
        const r = await axios.get("http://127.0.0.1:8000/restaurants/");
        setHotels(h.data || []);
        setRestaurants(r.data || []);
      } catch (err) {
        console.error("Erreur chargement données cartes", err);
      }
    })();
  }, []);

  // Localisation client en temps réel
  useEffect(() => {
    if (navigator.geolocation) {
      const watcher = navigator.geolocation.watchPosition(
        pos => {
          setUserPos([pos.coords.latitude, pos.coords.longitude]);
        },
        err => console.warn("Erreur GPS", err),
        { enableHighAccuracy: true, maximumAge: 5000, timeout: 10000 }
      );
      return () => navigator.geolocation.clearWatch(watcher);
    }
  }, []);

  // Point central par défaut (Kinshasa par exemple)
  const center = userPos || [-4.4419, 15.2663];

  return (
    <div className="min-h-screen p-6 bg-gray-50">
      <h1 className="text-2xl font-bold mb-4 text-[#0A1931]">
        Carte interactive
      </h1>

      <MapContainer center={center} zoom={13} style={{ height: "75vh", width: "100%" }}>
        {/* Fond de carte OpenStreetMap */}
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

        {/* Position du client */}
        {userPos && (
          <Marker position={userPos} icon={clientIcon}>
            <Popup>📍 Vous êtes ici</Popup>
          </Marker>
        )}

        {/* Hôtels */}
        {hotels.map(h => (
          h.latitude && h.longitude && (
            <Marker key={`h-${h.id}`} position={[h.latitude, h.longitude]} icon={hotelIcon}>
              <Popup>
                <b>🏨 Hôtel :</b> {h.name} <br />
                📍 {h.address} <br />
                💵 {h.price_per_night} $/nuit
                <br />
                <a
                  href={`/hotels/${h.id}/rooms`}
                  className="text-blue-600 underline"
                >
                  Réserver →
                </a>
              </Popup>
            </Marker>
          )
        ))}

        {/* Restaurants */}
        {restaurants.map(r => (
          r.latitude && r.longitude && (
            <Marker key={`r-${r.id}`} position={[r.latitude, r.longitude]} icon={restaurantIcon}>
              <Popup>
                <b>🍽️ Restaurant :</b> {r.name} <br />
                📍 {r.address}
                <br />
                <a
                  href={`/restaurants/${r.id}/menus`}
                  className="text-blue-600 underline"
                >
                  Voir le menu →
                </a>
              </Popup>
            </Marker>
          )
        ))}
      </MapContainer>
    </div>
  );
}
