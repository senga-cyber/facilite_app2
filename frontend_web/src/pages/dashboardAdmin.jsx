// frontend_web/src/pages/dashboardAdmin.jsx
import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  CartesianGrid, ResponsiveContainer, PieChart, Pie, Cell
} from "recharts";
import api from "../api/client";

export default function DashboardAdmin() {
  const [stats, setStats] = useState({ orders: [], payments: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [orders, payments] = await Promise.all([
          api.get("/orders/"),
          api.get("/payments/")
        ]);
        setStats({ orders: orders.data, payments: payments.data });
      } catch (err) {
        console.error(err);
        setError("Impossible de charger les statistiques.");
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const ordersData = stats.orders.map(o => ({
    name: `Commande ${o.id}`,
    total: o.total
  }));

  const paymentData = stats.payments.map(p => ({
    name: p.payment_method,
    value: p.amount
  }));

  const COLORS = ["#FFD700", "#0A1931", "#00C49F", "#FF8042", "#0088FE", "#FFBB28"];

  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 p-6 bg-gray-50">
        <h1 className="text-2xl font-bold text-[#0A1931] mb-4">
          Admin Panel - Statistiques
        </h1>

        {loading && <p>Chargement...</p>}
        {error && <p className="text-red-500">{error}</p>}

        {!loading && !error && (
          <div className="grid md:grid-cols-2 gap-6">
            {/* Graphique commandes */}
            <div className="bg-white shadow rounded-lg p-4">
              <h2 className="text-lg font-semibold mb-2">Commandes</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={ordersData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="total" fill="#0A1931" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Graphique paiements */}
            <div className="bg-white shadow rounded-lg p-4">
              <h2 className="text-lg font-semibold mb-2">Paiements</h2>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={paymentData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={100}
                    dataKey="value"
                    label
                  >
                    {paymentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
