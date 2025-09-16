// frontend_web/src/App.jsx
import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import  AuthProvider  from "./context/AuthContext";
import PrivateRoute from "./utils/PrivateRoute";
import RoleRoute from "./utils/RoleRoute";

import Navbar from "./components/Navbar";

// Pages
import Login from "./pages/login";
import Register from "./pages/register";
import Dashboard from "./pages/dashboard";
import DashboardAdmin from "./pages/dashboardAdmin";
import DashboardHotel from "./pages/dashboardHotel";
import DashboardRestaurant from "./pages/dashboardRestaurant";
import DashboardClient from "./pages/dashboardClient";
import Restaurants from "./pages/restaurants";
import Menus from "./pages/menus";
import PaymentPage from "./pages/PaymentPage";
import HotelsPage from "./pages/HotelsPage";
import RoomsPage from "./pages/RoomsPage";
import MapView from "./pages/MapView";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Public */}
          <Route path="/hotels" element={<HotelsPage />} />
          <Route path="/hotels/:hotelId/rooms" element={<RoomsPage />} />
          <Route path="/restaurants" element={<Restaurants />} />
          <Route path="/restaurants/:id/menus" element={<Menus />} />
          <Route path="/payment" element={<PaymentPage />} />
          <Route path="/map" element={<MapView />} />

          {/* Auth */}
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />

          {/* Rôles */}
          <Route
            path="/dashboard/admin"
            element={
              <RoleRoute allow={["admin"]}>
                <DashboardAdmin />
              </RoleRoute>
            }
          />
          <Route
            path="/dashboard/hotel"
            element={
              <RoleRoute allow={["hotel_manager", "admin"]}>
                <DashboardHotel />
              </RoleRoute>
            }
          />
          <Route
            path="/dashboard/restaurant"
            element={
              <RoleRoute allow={["restaurant_manager", "admin"]}>
                <DashboardRestaurant />
              </RoleRoute>
            }
          />
          <Route
            path="/dashboard/client"
            element={
              <RoleRoute allow={["client"]}>
                <DashboardClient />
              </RoleRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
