import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api/client";

export default function Menus() {
  const { id } = useParams();
  const [items, setItems] = useState([]);

  useEffect(() => {
    api.get(`/restaurants/${id}/menu`)
      .then((res) => setItems(res.data || []))
      .catch(() => setItems([]));
  }, [id]);

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold text-[#0A1931] mb-4">Menu du restaurant #{id}</h1>
      <div className="space-y-3">
        {items.map((m) => (
          <div key={m.id} className="bg-white border rounded-xl p-4 flex items-center justify-between">
            <div>
              <div className="font-semibold">{m.name}</div>
              {m.description && <div className="text-gray-500 text-sm">{m.description}</div>}
            </div>
            <div className="text-[#0A1931] font-bold">{m.price.toFixed(2)} $</div>
          </div>
        ))}
        {items.length === 0 && <p>Aucun plat pour le moment.</p>}
      </div>
    </div>
  );
}
