/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#11151C",
        panel: "#171C26",
        panel2: "#1D2330",
        line: "#2A3140",
        paper: "#F4F1EA",
        amber: "#F0A93A",
        signal: "#3FCFA0",
        alert: "#E2604F",
        muted: "#8993A6",
      },
      fontFamily: {
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
}

