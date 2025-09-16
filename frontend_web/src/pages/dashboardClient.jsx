// frontend_web/src/pages/dashboardClient.jsx
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";

export default function DashboardClient() {
  const [reservations, setReservations] = useState([]);
  const [orders, setOrders] = useState([]);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [res, ord, pay] = await Promise.all([
          api.get("/reservations/me"),
          api.get("/orders/me"),
          api.get("/payments/me"),
        ]);
        setReservations(res.data);
        setOrders(ord.data);
        setPayments(pay.data);
      } catch (err) {
        console.error("Erreur chargement données client", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <p className="p-6">Chargement...</p>;

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-2xl font-bold text-[#0A1931] mb-6">
        Mon espace client
      </h1>

      {/* Réservations */}
      <section className="mb-6">
        <h2 className="text-lg font-semibold mb-2">Mes réservations</h2>
        <div className="bg-white shadow rounded-lg p-4">
          {reservations.length === 0 ? (
            <p>Aucune réservation pour le moment.</p>
          ) : (
            <ul className="space-y-2">
              {reservations.map((r) => (
                <li
                  key={r.id}
                  className="border-b py-2 flex justify-between items-center"
                >
                  <div>
                    Hôtel #{r.hotel_id} —{" "}
                    {new Date(r.check_in).toLocaleDateString()} →{" "}
                    {new Date(r.check_out).toLocaleDateString()}{" "}
                    <span className="font-semibold ml-2">
                      {r.total_price} $
                    </span>
                  </div>
                  <button
                    onClick={() =>
                      navigate(`/map?reservationId=${r.id}`)
                    }
                    className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Localiser
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>

      {/* Commandes */}
      <section className="mb-6">
        <h2 className="text-lg font-semibold mb-2">Mes commandes</h2>
        <div className="bg-white shadow rounded-lg p-4">
          {orders.length === 0 ? (
            <p>Aucune commande pour le moment.</p>
          ) : (
            <ul className="space-y-2">
              {orders.map((o) => (
                <li
                  key={o.id}
                  className="border-b py-2 flex justify-between items-center"
                >
                  <div>
                    Commande #{o.id} —{" "}
                    <span className="font-semibold">{o.total} $</span>
                  </div>
                  <button
                    onClick={() =>
                      navigate(`/map?orderId=${o.id}`)
                    }
                    className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
                  >
                    Localiser
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>

      {/* Paiements */}
      <section>
        <h2 className="text-lg font-semibold mb-2">Mes paiements</h2>
        <div className="bg-white shadow rounded-lg p-4">
          {payments.length === 0 ? (
            <p>Aucun paiement enregistré.</p>
          ) : (
            <ul className="space-y-2">
              {payments.map((p) => (
                <li key={p.id} className="border-b py-2">
                  {p.payment_method.toUpperCase()} —{" "}
                  <span className="font-semibold ml-2">
                    {p.amount} $
                  </span>{" "}
                  (code: {p.transaction_code})
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </div>
  );
}
