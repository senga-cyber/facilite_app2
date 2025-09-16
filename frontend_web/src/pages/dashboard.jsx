import React from "react";
import { useNavigate } from "react-router-dom";

function Dashboard() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token"); // ✅ Déconnexion
    navigate("/login");
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-50">
      <h1 className="text-3xl font-bold text-gray-800">Bienvenue sur le Dashboard 🎉</h1>
      <p className="mt-2 text-gray-600">Vous êtes connecté avec succès !</p>
      <button
        onClick={handleLogout}
        className="mt-6 bg-red-500 text-white px-6 py-2 rounded-lg hover:bg-red-600 transition"
      >
        Se déconnecter
      </button>
    </div>
  );
}

export default Dashboard;
