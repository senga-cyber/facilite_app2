import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import logo from "../assets/logo.png";

function Register() {
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/register/client", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          phone_number: phone,
          password,
        }),
      });

      if (!response.ok) {
        throw new Error("Échec de l’inscription");
      }

      alert("Inscription réussie ! Vous pouvez vous connecter.");
      navigate("/login");
    } catch (error) {
      alert(error.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0A1931]">
      <div className="bg-white shadow-xl rounded-2xl p-10 w-full max-w-md border-t-8 border-[#FFD700]">
        {/* Logo + Titre */}
        <div className="flex flex-col items-center mb-6">
          <img src={logo} alt="Logo" className="w-20 h-20 object-contain mb-3" />
          <h1 className="text-3xl font-extrabold text-[#0A1931]">Facilite</h1>
          <p className="text-gray-500">Créer un compte</p>
        </div>

        {/* Form */}
        <form onSubmit={handleRegister} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-600">
              Nom complet
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="mt-1 w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-[#FFD700] focus:outline-none"
              placeholder="Ex: Chadrack nsenga"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600">
              Numéro de téléphone
            </label>
            <input
              type="text"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="mt-1 w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-[#FFD700] focus:outline-none"
              placeholder="0999887766"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600">
              Mot de passe
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-[#FFD700] focus:outline-none"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            className="w-full bg-[#FFD700] text-black font-bold py-2 rounded-lg shadow-lg hover:bg-[#0A1931] hover:text-white transition duration-300"
          >
            S’inscrire
          </button>
        </form>

        {/* Login */}
        <p className="mt-6 text-center text-gray-500 text-sm">
          Déjà inscrit ?{" "}
          <a href="/login" className="text-[#FFD700] font-semibold hover:underline">
            Se connecter
          </a>
        </p>
      </div>
    </div>
  );
}

export default Register;
