// frontend_web/src/pages/login.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";
import useAuth from "../hooks/useAuth";
import logo from "../assets/logo.png";

export default function Login() {
  const { login, setLoading, loading } = useAuth();
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [asManager, setAsManager] = useState(false);
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      let res;
      if (asManager) {
        res = await api.post("/auth/login/manager", {
          phone_number: phone,
          password,
        });
      } else {
        res = await api.post("/auth/login/client", { phone_number: phone });
      }

      console.log("Login response:", res.data); // 👈 debug

      const { access_token, role, user } = res.data;
      login({
        token: access_token,
        role: role || user?.role || "client",
        user: user || null,
      });

      const r = role || user?.role || "client";
      if (r === "admin") navigate("/dashboard/admin");
      else if (r === "hotel_manager") navigate("/dashboard/hotel");
      else if (r === "restaurant_manager") navigate("/dashboard/restaurant");
      else navigate("/dashboard/client");
    } catch (err) {
      console.error("Login error:", err?.response?.data || err.message);
      setMessage(err?.response?.data?.detail || "❌ Erreur de connexion");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 px-4">
      <div className="bg-white shadow-2xl rounded-2xl p-8 w-full max-w-md border-t-4 border-sky-500 animate-fade-in">
        
        {/* Logo + Titre */}
        <div className="flex flex-col items-center mb-6">
          <img src={logo} alt="Logo" className="logo" />
          <h1 className="text-2xl font-extrabold text-slate-900">FACILITE</h1>
          <p className="text-gray-500 text-sm">Connexion à votre compte</p>
        </div>

        {/* Formulaire */}
        <form onSubmit={submit} className="space-y-5">
          <div className="flex flex-col">
            <label className="block text-sm text-gray-700 mb-1">
              Numéro de téléphone
            </label>
            <input
              className="w-full px-4 py-3 rounded-lg border border-gray-300 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-sky-500"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+(code) 9********0"
              required
            />
          </div>

          {asManager && (
            <div>
              <label className="block text-sm text-gray-700 mb-1">
                Mot de passe (manager)
              </label>
              <input
                type="password"
                className="w-full px-4 py-3 rounded-lg border border-gray-300 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-sky-500"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required={asManager}
              />
            </div>
          )}

          {/* Options */}
          <div className="flex items-center justify-between text-sm">
            <label className="flex items-center gap-2 text-gray-600">
              <input
                type="checkbox"
                checked={asManager}
                onChange={(e) => setAsManager(e.target.checked)}
                className="h-4 w-4 text-sky-500 focus:ring-sky-500 rounded"
              />
              <span>Je suis manager / admin</span>
            </label>
            <a href="/register" className="text-sky-500 hover:underline font-medium">
              Créer un compte
            </a>
          </div>

          {/* Bouton */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-lg font-bold transition bg-sky-500 hover:bg-sky-600 text-white shadow-md"
          >
            {loading ? "Connexion..." : "Se connecter"}
          </button>
        </form>

        {/* Message */}
        {message && (
          <p className="mt-4 text-center text-sm font-medium text-red-500">
            {typeof message === "string" ? message : JSON.stringify(message)}
          </p>
        )}
      </div>
    </div>
  );
}
