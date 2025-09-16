// frontend_web/src/pages/dashboardHotel.jsx
import React, { useEffect, useState } from "react";
import api from "../api/client";
import Sidebar from "../components/Sidebar";

export default function DashboardHotel() {
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");
  const [hotels, setHotels] = useState([]);

  const fetchHotels = async () => {
    try {
      const res = await api.get("/hotels/me"); // ✅ route qui renvoie les hôtels du manager
      setHotels(res.data);
    } catch (err) {
      console.error("Erreur chargement hôtels", err);
    }
  };

  useEffect(() => {
    fetchHotels();
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    try {
      await api.post("/hotels/", { name, address });
      alert("Hôtel créé !");
      setName("");
      setAddress("");
      fetchHotels();
    } catch (err) {
      alert(err?.response?.data?.detail || "Erreur");
    }
  };

  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 p-6 bg-gray-50">
        <h1 className="text-2xl font-bold mb-4">Gestion des Hôtels</h1>

        {/* Formulaire création hôtel */}
        <form
          onSubmit={submit}
          className="bg-white p-6 shadow rounded-lg space-y-4 max-w-md mb-6"
        >
          <div>
            <label className="block text-sm font-medium">Nom</label>
            <input
              className="border w-full p-2 rounded"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium">Adresse</label>
            <input
              className="border w-full p-2 rounded"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              required
            />
          </div>
          <button className="bg-[#0A1931] text-white px-4 py-2 rounded">
            Ajouter
          </button>
        </form>

        {/* Liste des hôtels */}
        <div className="bg-white p-6 shadow rounded-lg">
          <h2 className="text-lg font-semibold mb-2">Mes hôtels</h2>
          {hotels.length === 0 ? (
            <p>Aucun hôtel enregistré.</p>
          ) : (
            <ul className="space-y-2">
              {hotels.map((h) => (
                <li
                  key={h.id}
                  className="border-b py-2 flex justify-between items-center"
                >
                  <span>
                    {h.name} — {h.address}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </main>
    </div>
  );
}
