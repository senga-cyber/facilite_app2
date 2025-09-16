import React, { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { useLocation, useSearchParams } from "react-router-dom";

// Logos (assure-toi qu'ils soient bien dans src/assets/)
import airtel from "../assets/airtel.png";
import orange from "../assets/orange.png";
import mpesa from "../assets/mpesa.png";
import visa from "../assets/visa.png";
import mastercard from "../assets/mastercard.png";
import cash from "../assets/cash.png";

const METHODS = [
  { name: "airtel_money", label: "Airtel Money", icon: airtel },
  { name: "orange_money", label: "Orange Money", icon: orange },
  { name: "mpesa", label: "M-Pesa", icon: mpesa },
  { name: "visa", label: "Visa", icon: visa },
  { name: "mastercard", label: "Mastercard", icon: mastercard },
  { name: "cash", label: "Cash", icon: cash },
];

const API_BASE = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000";

export default function PaymentPage() {
  const location = useLocation();
  const [searchParams] = useSearchParams();

  // Pré-remplissage depuis navigate(..., { state }) ou query string
  const prefilled = useMemo(() => {
    const st = location.state || {};
    return {
        amount: st.amount ?? (parseFloat(searchParams.get("amount")) || ""),
        order_id: st.order_id ?? (parseInt(searchParams.get("order_id"), 10) || null),
        reservation_id: st.reservation_id ?? (parseInt(searchParams.get("reservation_id"), 10) || null),

    };
  }, [location.state, searchParams]);

  const [amount, setAmount] = useState(prefilled.amount);
  const [orderId, setOrderId] = useState(prefilled.order_id);
  const [reservationId, setReservationId] = useState(prefilled.reservation_id);
  const [paymentMethod, setPaymentMethod] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [qrUrl, setQrUrl] = useState(null);
  const [txCode, setTxCode] = useState(null);

  useEffect(() => {
    setAmount(prefilled.amount);
    setOrderId(prefilled.order_id);
    setReservationId(prefilled.reservation_id);
  }, [prefilled]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setQrUrl(null);
    setTxCode(null);

    if (!amount || !paymentMethod) {
      setMessage("⚠️ Veuillez indiquer un montant et choisir un mode de paiement.");
      return;
    }

    if (!orderId && !reservationId) {
      setMessage("⚠️ Le paiement doit être lié à une commande ou une réservation.");
      return;
    }

    try {
      setLoading(true);
      const token = localStorage.getItem("token") || "";

      const res = await axios.post(
        `${API_BASE}/payments/`,
        {
          amount: parseFloat(amount),
          payment_method: paymentMethod,
          order_id: orderId || null,
          reservation_id: reservationId || null,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      const data = res.data;
      setTxCode(data.transaction_code || null);
      setQrUrl(data.qr_url || null);
      setMessage("✅ Paiement réussi !");
    } catch (err) {
      console.error(err);
      setMessage(`❌ Erreur : ${err?.response?.data?.detail || "Impossible de traiter le paiement"}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0d1b2a] p-4">
      <div className="bg-white w-full max-w-2xl rounded-2xl shadow-xl p-6 md:p-8">
        {/* En-tête */}
        <div className="flex items-center justify-center gap-3 mb-6">
          <img src="/logo192.png" alt="Facilite" className="h-10 w-10 rounded-full ring-1 ring-[#d4af37]" />
          <h1 className="text-2xl md:text-3xl font-bold text-[#0d1b2a]">
            Paiement sécurisé
          </h1>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Montant */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Montant (USD)
            </label>
            <input
              type="number"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#d4af37]"
              placeholder="Ex: 120.00"
              required
              readOnly={Boolean(prefilled.amount)}
            />
            {prefilled.amount && (
              <p className="text-xs text-gray-500 mt-1">Montant fixé par la réservation/commande.</p>
            )}
          </div>

          {/* Modes de paiement */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Choisissez un mode de paiement
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {METHODS.map((m) => (
                <button
                  key={m.name}
                  type="button"
                  onClick={() => setPaymentMethod(m.name)}
                  className={`flex flex-col items-center gap-2 rounded-xl border p-3 transition hover:shadow ${
                    paymentMethod === m.name ? "border-[#d4af37] bg-yellow-50" : "border-gray-300"
                  }`}
                >
                  <img src={m.icon} alt={m.label} className="h-10 w-10" />
                  <span
                    className={`text-sm font-medium ${
                      paymentMethod === m.name ? "text-[#0d1b2a]" : "text-gray-700"
                    }`}
                  >
                    {m.label}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Bouton payer */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-[#d4af37] text-black font-semibold hover:bg-yellow-600 transition disabled:opacity-60"
          >
            {loading ? "Traitement du paiement..." : "Payer maintenant"}
          </button>
        </form>

        {/* Message */}
        {message && (
          <div className="mt-4 text-center">
            <p className={`text-sm font-medium ${message.startsWith("✅") ? "text-green-600" : "text-red-600"}`}>
              {message}
            </p>
          </div>
        )}

        {/* QR Code */}
        {txCode && (
          <div className="mt-6 bg-gray-50 border border-gray-200 rounded-xl p-4">
            <p className="text-sm text-gray-700">
              <span className="font-semibold">Code transaction :</span>{" "}
              <span className="text-[#0d1b2a]">{txCode}</span>
            </p>
            {qrUrl && (
              <div className="mt-4 flex flex-col md:flex-row items-center gap-4">
                <img
                  src={qrUrl.startsWith("http") ? qrUrl : `${API_BASE}${qrUrl}`}
                  alt="QR Paiement"
                  className="h-40 w-40 rounded-lg border"
                />
                <a
                  href={qrUrl.startsWith("http") ? qrUrl : `${API_BASE}${qrUrl}`}
                  download
                  className="inline-block mt-3 px-4 py-2 rounded-lg border border-[#d4af37] text-[#d4af37] hover:bg-yellow-50"
                >
                  Télécharger le QR (PNG)
                </a>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
// frontend_web/src/pages/PaymentPage.jsx