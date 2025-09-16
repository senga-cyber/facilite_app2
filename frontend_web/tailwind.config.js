/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",   // dis à Tailwind où chercher tes classes
  ],
  theme: {
    extend: {
      colors: {
        gold: "#d4af37",
        nightblue: "#0d1b2a",
      },
      fontFamily: {
        inter: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};
