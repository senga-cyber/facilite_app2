// frontend_web/src/pages/RoomsPage.jsx
import React from "react";
import axios from "axios";
import { getPositionOnce } from "../utils/geoloc";
import { useNavigate } from "react-router-dom";

const API_BASE = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000";

function RoomCard({ room, hotelId }) {
  const navigate = useNavigate();

  const handleReserve = async () => {
    try {
      const token =
        localStorage.getItem("token") ||
        localStorage.getItem("access_token") ||
        "";

      const pos = await getPositionOnce();

      // 1️⃣ Crée une réservation dans le backend
      const res = await axios.post(
        `${API_BASE}/reservations/`,
        {
          hotel_id: hotelId,
          check_in: new Date().toISOString(),
          check_out: new Date(Date.now() + 24 * 3600 * 1000).toISOString(), // +1 jour
          latitude: pos?.latitude ?? null,
          longitude: pos?.longitude ?? null,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const reservationId = res.data.id;
      const amount = room.price_per_night;

      // 2️⃣ Redirection vers PaymentPage avec pré-remplissage
      navigate("/payment", {
        state: {
          reservation_id: reservationId,
          amount: amount,
        },
      });
    } catch (err) {
      console.error("Erreur réservation :", err);
      alert(err?.response?.data?.detail || "Impossible de réserver la chambre.");
    }
  };

  return (
    <div className="border rounded-xl shadow-sm p-4 bg-white text-nightblue">
      <div className="font-semibold text-lg mb-1">Chambre {room.room_number}</div>
      <div className="text-sm">Capacité : {room.capacity} personnes</div>
      <div className="text-sm font-medium text-gold mb-3">
        Prix : {room.price_per_night} $
      </div>
      <button
        onClick={handleReserve}
        className="w-full py-2 rounded-lg bg-gold text-black font-semibold hover:bg-yellow-600 transition"
      >
        Réserver
      </button>
    </div>
  );
}

export default function RoomsPage({ rooms = [], hotelId }) {
  return (
    <div className="min-h-screen bg-nightblue p-6">
      <h1 className="text-2xl font-bold text-white mb-6">
        Chambres disponibles
      </h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {rooms.map((room) => (
          <RoomCard key={room.id} room={room} hotelId={hotelId} />
        ))}
      </div>
    </div>
  );
}
