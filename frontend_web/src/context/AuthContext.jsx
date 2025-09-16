// frontend_web/src/context/AuthContext.jsx
import React, { createContext, useState, useEffect } from "react";

// Création du contexte
export const AuthContext = createContext();

// Fournisseur d'authentification
export default function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("token") || null);
  const [role, setRole] = useState(localStorage.getItem("role") || null);
  const [loading, setLoading] = useState(false);

  // 🔑 Raccourci : connecté ou pas
  const isAuthenticated = !!token;

  const login = ({ token, role, user }) => {
    setToken(token);
    setRole(role);
    setUser(user);
    localStorage.setItem("token", token);
    localStorage.setItem("role", role);
  };

  const logout = () => {
    setToken(null);
    setRole(null);
    setUser(null);
    localStorage.removeItem("token");
    localStorage.removeItem("role");
  };

  // 🔄 Synchroniser automatiquement quand token change
  useEffect(() => {
    if (!token) {
      setUser(null);
      setRole(null);
    }
  }, [token]);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        role,
        isAuthenticated,
        login,
        logout,
        loading,
        setLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
