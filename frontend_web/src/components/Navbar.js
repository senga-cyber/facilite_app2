// frontend_web/src/components/Navbar.jsx
import React from "react";
import { Link, useLocation } from "react-router-dom";
import useAuth from "../hooks/useAuth";
import logo from "../assets/logo.png";

export default function Navbar() {
  const { token, role, logout } = useAuth();
  const { pathname } = useLocation();

  // Cacher la navbar sur login/register
  const hide = ["/login", "/register"].includes(pathname);
  if (hide) return null;

  return (
    <header className="bg-white border-b border-gray-100 sticky top-0 z-30 shadow-sm">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        {/* Logo + redirection */}
        <Link to={token ? "/dashboard" : "/login"} className="flex items-center gap-3">
          <img src={logo} alt="logo" className="w-8 h-8 object-contain" />
          <span className="font-extrabold text-[#0A1931]">Facilite</span>
        </Link>

        {/* Navigation */}
        <nav className="flex items-center gap-4 text-sm">
          <Link to="/restaurants" className="text-gray-700 hover:text-[#0A1931]">
            Restaurants
          </Link>

          {token ? (
            <>
              {role === "admin" && (
                <Link to="/dashboard/admin" className="text-gray-700 hover:text-[#0A1931]">
                  Admin
                </Link>
              )}
              {role === "hotel_manager" && (
                <Link to="/dashboard/hotel" className="text-gray-700 hover:text-[#0A1931]">
                  Hôtels
                </Link>
              )}
              {role === "restaurant_manager" && (
                <Link to="/dashboard/restaurant" className="text-gray-700 hover:text-[#0A1931]">
                  Restos
                </Link>
              )}
              {role === "client" && (
                <Link to="/dashboard/client" className="text-gray-700 hover:text-[#0A1931]">
                  Mon espace
                </Link>
              )}
              <button
                onClick={logout}
                className="ml-2 bg-[#0A1931] text-white px-3 py-1.5 rounded hover:opacity-90"
              >
                Déconnexion
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-gray-700 hover:text-[#0A1931]">
                Login
              </Link>
              <Link
                to="/register"
                className="text-white bg-[#FFD700] px-3 py-1.5 rounded hover:opacity-90"
              >
                S’inscrire
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
