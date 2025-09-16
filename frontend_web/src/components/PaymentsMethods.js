import React from "react";
import airtel from "../assets/airtel.png";
import orange from "../assets/orange.png";
import mpesa from "../assets/mpesa.png";
import visa from "../assets/visa.png";
import mastercard from "../assets/mastercard.png";
import cash from "../assets/cash.png";

export default function PaymentMethods() {
  const methods = [
    { name: "Airtel Money", icon: airtel },
    { name: "Orange Money", icon: orange },
    { name: "M-Pesa", icon: mpesa },
    { name: "Visa", icon: visa },
    { name: "Mastercard", icon: mastercard },
    { name: "Cash", icon: cash },
  ];

  return (
    <div className="bg-white rounded-lg shadow-md p-6 text-center">
      <h2 className="text-xl font-bold mb-4 text-gray-800">
        Choisissez un mode de paiement
      </h2>
      <div className="grid grid-cols-3 gap-6">
        {methods.map((m) => (
          <div
            key={m.name}
            className="flex flex-col items-center hover:scale-105 transition-transform cursor-pointer"
          >
            <img src={m.icon} alt={m.name} className="h-16 w-16 mb-2" />
            <span className="text-gray-700 font-medium">{m.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
