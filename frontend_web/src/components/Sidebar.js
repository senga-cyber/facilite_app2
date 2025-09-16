// frontend_web/src/components/Sidebar.js
import React from "react";
import { Link, useLocation } from "react-router-dom";
import useAuth from "../hooks/useAuth";

export default function Sidebar() {
  const { role, logout } = useAuth();
  const { pathname } = useLocation();

  const links = [
    { to: "/dashboard", label: "Accueil", roles: ["admin","hotel_manager","restaurant_manager","client"] },
    { to: "/dashboard/admin", label: "Admin Panel", roles: ["admin"] },
    { to: "/dashboard/hotel", label: "Hôtels", roles: ["admin","hotel_manager"] },
    { to: "/dashboard/restaurant", label: "Restaurants", roles: ["admin","restaurant_manager"] },
    { to: "/dashboard/client", label: "Mes commandes", roles: ["client"] },
  ];

  return (
    <aside className="bg-[#0A1931] text-white w-64 min-h-screen flex flex-col">
      <div className="p-4 font-bold text-lg border-b border-gray-700">Facilite</div>
      <nav className="flex-1">
        {links
          .filter(l => l.roles.includes(role))
          .map(l => (
            <Link
              key={l.to}
              to={l.to}
              className={`block px-4 py-2 hover:bg-[#FFD700] hover:text-black ${
                pathname === l.to ? "bg-[#FFD700] text-black" : ""
              }`}
            >
              {l.label}
            </Link>
          ))}
      </nav>
      <button
        onClick={logout}
        className="m-4 bg-red-600 hover:bg-red-700 rounded px-3 py-2"
      >
        Déconnexion
      </button>
    </aside>
  );
}
