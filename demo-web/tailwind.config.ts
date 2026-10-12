import type { Config } from "tailwindcss";

/**
 * Design tokens of the project page. Only these colours exist. The legacy palette names used by the
 * results components (slate, red, emerald, sky, blue, orange, amber) are mapped onto them:
 * neutrals stay neutral, the single accent is #1F5A96, and red/green are reserved for test outcomes
 * and fix / no-fix.
 */
const ink = "#18212B";
const muted = "#5B6673";
const rule = "#DCE1E7";
const panel = "#F4F6F8";
const accent = "#1F5A96";
const pass = "#2D7A4B";
const fail = "#B23B2C";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    colors: {
      transparent: "transparent",
      current: "currentColor",
      white: "#FFFFFF",
      ink, muted, rule, panel, accent, pass, fail,
      slate: { 50: panel, 100: panel, 200: rule, 300: rule, 400: muted, 500: muted, 600: muted, 700: ink, 800: ink, 900: ink },
      red: { 50: "#F7EAE8", 100: "#F7EAE8", 200: "#E3BDB7", 300: fail, 400: fail, 500: fail, 600: fail, 700: fail, 800: "#8E2E22", 900: "#8E2E22" },
      emerald: { 50: "#E8F2EC", 100: "#E8F2EC", 200: "#B5D5C2", 300: pass, 400: pass, 500: pass, 600: pass, 700: pass, 800: "#236039", 900: "#236039" },
      sky: { 50: "#EAF1F8", 100: "#EAF1F8", 200: "#B7CDE3", 300: accent, 400: accent, 500: accent, 600: accent, 700: accent, 800: "#174673", 900: "#174673" },
      blue: { 50: "#EAF1F8", 100: "#EAF1F8", 200: "#B7CDE3", 300: accent, 400: accent, 500: accent, 600: accent, 700: accent, 800: "#174673", 900: "#174673" },
      orange: { 50: "#EAF1F8", 100: "#EAF1F8", 200: "#B7CDE3", 300: accent, 400: accent, 500: accent, 600: accent, 700: accent, 800: "#174673", 900: "#174673" },
      amber: { 50: panel, 100: panel, 200: rule, 300: rule, 400: muted, 500: muted, 600: muted, 700: ink, 800: ink, 900: ink, 950: ink },
    },
    extend: {
      fontFamily: {
        serif: ["var(--font-serif)", "Georgia", "Cambria", "Times New Roman", "serif"],
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "Roboto", "Arial", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "SFMono-Regular", "Menlo", "Consolas", "Liberation Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
export default config;
