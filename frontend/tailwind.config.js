/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"],
      },
      colors: {
        accent: {
          DEFAULT: "#ff4500",
          hover:   "#ff5722",
          light:   "#ff6b35",
        },
        dark: {
          base:     "#0d1117",
          elevated: "#161b22",
          card:     "#1c2128",
          hover:    "#222831",
          border:   "#30363d",
        },
      },
      animation: {
        "fade-up":   "fadeUp 0.5s ease both",
        "fade-in":   "fadeIn 0.4s ease both",
        float:       "float 3s ease-in-out infinite",
        "pulse-dot": "pulseDot 2s ease-in-out infinite",
        shimmer:     "shimmer 1.4s infinite",
      },
      keyframes: {
        fadeUp: {
          "0%":   { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          "0%":   { opacity: "0" },
          "100%": { opacity: "1" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%":      { transform: "translateY(-6px)" },
        },
        pulseDot: {
          "0%, 100%": { opacity: "1", transform: "scale(1)" },
          "50%":      { opacity: "0.5", transform: "scale(1.4)" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      boxShadow: {
        "glow-sm": "0 0 12px rgba(255,69,0,0.2)",
        "glow-md": "0 0 24px rgba(255,69,0,0.3)",
        "glow-lg": "0 0 40px rgba(255,69,0,0.4)",
        card:      "0 4px 24px rgba(0,0,0,0.35)",
      },
      backgroundImage: {
        "accent-gradient": "linear-gradient(135deg, #ff4500, #ff6b35)",
        "hero-overlay":    "linear-gradient(to top, rgba(13,17,23,0.97) 0%, rgba(13,17,23,0.55) 55%, transparent 100%)",
        "shimmer-gradient":"linear-gradient(90deg, transparent 25%, rgba(255,255,255,0.05) 50%, transparent 75%)",
      },
    },
  },
  plugins: [],
};
