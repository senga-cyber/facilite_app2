// frontend_web/src/pages/dashboardRestaurant.jsx
import React, { useEffect, useState } from "react";
import api from "../api/client";
import Sidebar from "../components/Sidebar";

export default function DashboardRestaurant() {
  const [restaurantId, setRestaurantId] = useState("");
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [menus, setMenus] = useState([]);

  const fetchMenus = async () => {
    if (!restaurantId) return;
    try {
      const res = await api.get(`/restaurants/${restaurantId}/menus`);
      setMenus(res.data);
    } catch (err) {
      console.error("Erreur chargement menus", err);
    }
  };

  useEffect(() => {
    fetchMenus();
  }, [restaurantId]);

  const submit = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/menus/`, {
        restaurant_id: parseInt(restaurantId, 10),
        name,
        price: parseFloat(price),
      });
      alert("Plat ajouté !");
      setName("");
      setPrice("");
      fetchMenus();
    } catch (err) {
      alert(err?.response?.data?.detail || "Erreur");
    }
  };

  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 p-6 bg-gray-50">
        <h1 className="text-2xl font-bold mb-4">Gestion des Restaurants</h1>

        {/* Formulaire ajout menu */}
        <form
          onSubmit={submit}
          className="bg-white p-6 shadow rounded-lg space-y-4 max-w-md mb-6"
        >
          <div>
            <label>ID Restaurant</label>
            <input
              className="border w-full p-2 rounded"
              value={restaurantId}
              onChange={(e) => setRestaurantId(e.target.value)}
              required
            />
          </div>
          <div>
            <label>Nom du Plat</label>
            <input
              className="border w-full p-2 rounded"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div>
            <label>Prix</label>
            <input
              type="number"
              step="0.01"
              className="border w-full p-2 rounded"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              required
            />
          </div>
          <button className="bg-[#FFD700] text-black px-4 py-2 rounded">
            Ajouter
          </button>
        </form>

        {/* Liste des menus */}
        <div className="bg-white p-6 shadow rounded-lg">
          <h2 className="text-lg font-semibold mb-2">Menus du restaurant</h2>
          {menus.length === 0 ? (
            <p>Aucun menu pour ce restaurant.</p>
          ) : (
            <ul className="space-y-2">
              {menus.map((m) => (
                <li
                  key={m.id}
                  className="border-b py-2 flex justify-between items-center"
                >
                  <span>
                    {m.name} — <strong>{m.price} $</strong>
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
