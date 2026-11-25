import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Modern SaaS Theme Palette (inspired by the reference dashboard)
        brand: {
          50: "#EFF6FF",
          100: "#DBEAFE",
          200: "#BFDBFE",
          300: "#93C5FD",
          400: "#60A5FA",
          500: "#3B82F6",
          600: "#2563EB",
          700: "#1D4ED8",
          800: "#1E40AF",
          900: "#1E3A8A",
        },
        surface: {
          bg: "#F8FAFC", // soft off-white/slate dashboard canvas
          card: "#FFFFFF", // pure white cards
          cardHover: "#FAFAFA",
          subtle: "#F1F5F9", // secondary soft panel
          border: "#E2E8F0", // delicate border
          borderLight: "#F1F5F9",
        },
        // Backwards compatibility mappings for existing swiss-* classes to seamlessly adapt
        swiss: {
          bg: "#F8FAFC",
          panel: "#F1F5F9",
          card: "#FFFFFF",
          yellow: "#2563EB", // remapped to modern primary blue
          yellowHover: "#1D4ED8",
          black: "#0F172A", // modern slate-900
          muted: "#64748B", // modern slate-500
          line: "#E2E8F0",
          border: "#E2E8F0",
          accentBlue: "#EFF6FF",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
        mono: [
          "JetBrains Mono",
          "SFMono-Regular",
          "Menlo",
          "Monaco",
          "Consolas",
          "monospace",
        ],
      },
      borderRadius: {
        "xl": "12px",
        "2xl": "16px",
        "3xl": "20px",
      },
      boxShadow: {
        sm: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        DEFAULT: "0 1px 3px 0 rgba(0, 0, 0, 0.08), 0 1px 2px -1px rgba(0, 0, 0, 0.05)",
        md: "0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -2px rgba(0, 0, 0, 0.05)",
        lg: "0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.04)",
        card: "0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05)",
        // Remap brutal shadows to soft subtle modern shadows
        brutal: "0 1px 3px 0 rgba(0, 0, 0, 0.06), 0 1px 2px -1px rgba(0, 0, 0, 0.04)",
        "brutal-sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        "brutal-lg": "0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.04)",
      },
    },
  },
  plugins: [],
};
export default config;
