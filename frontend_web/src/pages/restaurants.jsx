import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";

export default function Restaurants() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/restaurants/")
      .then((res) => setData(res.data || []))
      .catch(() => setData([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-6 text-center">Chargement...</div>;

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold text-[#0A1931] mb-4">Restaurants</h1>
      <div className="grid md:grid-cols-3 gap-4">
        {data.map((r) => (
          <div key={r.id} className="bg-white rounded-xl border p-4 hover:shadow-lg transition">
            <h3 className="font-bold text-lg">{r.name}</h3>
            <p className="text-sm text-gray-600">{r.address || "Adresse non renseignée"}</p>
            <Link to={`/restaurants/${r.id}/menus`} className="inline-block mt-3 text-sm text-white bg-[#0A1931] px-3 py-1.5 rounded">
              Voir le menu
            </Link>
          </div>
        ))}
        {data.length === 0 && <p>Aucun restaurant pour le moment.</p>}
      </div>
    </div>
  );
}
