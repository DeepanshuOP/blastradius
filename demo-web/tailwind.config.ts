import type { Config } from "tailwindcss";

/**
 * Design tokens of the BlastRadius site (Live Lab control room, D-65). Every colour is a CSS variable holding an
 * `r g b` triplet (defined in app/globals.css for the dark default and the light theme), so one class works in both
 * themes and opacity modifiers (`bg-red/20`) work. The palette is the slide deck's:
 * background #131722, panels #1B1F2A, accent #E8572A (the change, and risk), amber #F2A93B, blue #2F7FB0,
 * green #2E9E6A, red #C23B30.
 *
 * The legacy palette names used by the Evidence components (slate, red, emerald, sky, blue, orange, amber) are
 * mapped onto these: neutrals stay neutral, tints are the colour at low opacity.
 */
const c = (name: string) => `rgb(var(--${name}-rgb) / <alpha-value>)`;
const ink = c("ink");
const muted = c("muted");
const rule = c("rule");
const panel2 = c("panel2");

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    colors: {
      transparent: "transparent",
      current: "currentColor",
      white: "#FFFFFF",
      page: c("page"), panel: c("panel"), panel2, ink, muted, rule,
      accent: c("accent"), green: c("green"),
      amber: { DEFAULT: c("amber"), 50: "rgb(var(--amber-rgb) / 0.12)", 100: "rgb(var(--amber-rgb) / 0.16)", 200: "rgb(var(--amber-rgb) / 0.4)", 300: c("amber"), 400: c("amber"), 500: c("amber"), 600: c("amber"), 700: c("amber"), 800: c("amber"), 900: c("amber") },
      pass: c("green"), fail: c("red"),
      slate: { 50: panel2, 100: panel2, 200: rule, 300: rule, 400: muted, 500: muted, 600: muted, 700: ink, 800: ink, 900: ink },
      red: { DEFAULT: c("red"), 50: "rgb(var(--red-rgb) / 0.12)", 100: "rgb(var(--red-rgb) / 0.16)", 200: "rgb(var(--red-rgb) / 0.4)", 300: c("red"), 400: c("red"), 500: c("red"), 600: c("red"), 700: c("red-text"), 800: c("red-text"), 900: c("red-text") },
      emerald: { 50: "rgb(var(--green-rgb) / 0.12)", 100: "rgb(var(--green-rgb) / 0.16)", 200: "rgb(var(--green-rgb) / 0.4)", 300: c("green"), 400: c("green"), 500: c("green"), 600: c("green"), 700: c("green-text"), 800: c("green-text"), 900: c("green-text") },
      sky: { 50: "rgb(var(--blue-rgb) / 0.12)", 100: "rgb(var(--blue-rgb) / 0.16)", 200: "rgb(var(--blue-rgb) / 0.4)", 300: c("blue"), 400: c("blue"), 500: c("blue"), 600: c("blue"), 700: c("blue-text"), 800: c("blue-text"), 900: c("blue-text") },
      blue: { 50: "rgb(var(--blue-rgb) / 0.12)", 100: "rgb(var(--blue-rgb) / 0.16)", 200: "rgb(var(--blue-rgb) / 0.4)", DEFAULT: c("blue"), 300: c("blue"), 400: c("blue"), 500: c("blue"), 600: c("blue"), 700: c("blue-text"), 800: c("blue-text"), 900: c("blue-text") },
      orange: { 50: "rgb(var(--accent-rgb) / 0.12)", 100: "rgb(var(--accent-rgb) / 0.16)", 200: "rgb(var(--accent-rgb) / 0.4)", 300: c("accent"), 400: c("accent"), 500: c("accent"), 600: c("accent"), 700: c("accent"), 800: c("accent"), 900: c("accent") },
    },
    extend: {
      screens: { wide: "1400px", lab: "1440px" },
      fontSize: Object.fromEntries(["2xs", "xs", "sm", "base", "md", "lg", "xl", "2xl", "3xl"].map((k) => [k, [`var(--fs-${k})`, { lineHeight: `var(--lh-${k})` }]])),
      spacing: Object.fromEntries([["0.5", "0-5"], ["1", "1"], ["1.5", "1-5"], ["2", "2"], ["2.5", "2-5"], ["3", "3"], ["4", "4"], ["5", "5"], ["6", "6"], ["8", "8"], ["10", "10"], ["12", "12"], ["16", "16"]].map(([k, v]) => [k, `var(--space-${v})`])),
      fontFamily: {
        serif: ["var(--font-sans)", "ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "Roboto", "Arial", "sans-serif"],
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "Roboto", "Arial", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "SFMono-Regular", "Menlo", "Consolas", "Liberation Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
export default config;
