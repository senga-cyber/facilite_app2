import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

export default function HotelsPage() {
  const [hotels, setHotels] = useState([]);

  useEffect(() => {
    axios.get("http://127.0.0.1:8000/hotels/")
      .then((res) => setHotels(res.data))
      .catch((err) => console.error(err));
  }, []);

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold mb-6 text-nightblue">Liste des Hôtels</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {hotels.map((hotel) => (
          <div key={hotel.id} className="bg-white shadow-lg rounded-lg p-5 hover:shadow-xl transition">
            <h2 className="text-xl font-bold text-gold">{hotel.name}</h2>
            <p className="text-gray-600">{hotel.address}</p>
            <p className="text-gray-600 italic">{hotel.city}</p>
            <p className="mt-2 text-nightblue font-semibold">
              Prix / nuit : {hotel.price_per_night} USD
            </p>
            <Link
              to={`/hotels/${hotel.id}/rooms`}
              className="mt-4 inline-block bg-gold text-white py-2 px-4 rounded-lg hover:bg-yellow-600 transition"
            >
              Voir les chambres
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
