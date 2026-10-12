// Offline fallback for next/font/google: `NEXT_FONT_GOOGLE_MOCKED_RESPONSES=font-fallback.js npm run build`.
// Used by analysis/demo_check.py only when Google Fonts cannot be reached; the page then uses the local font stack.
const css = (family) => `@font-face { font-family: '${family}'; font-style: normal; font-weight: 400; font-display: swap; src: local('${family}'); }`;
module.exports = {
  "https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@200..900&display=swap": css("Source Serif 4"),
  "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap": css("IBM Plex Mono"),
  "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap": css("IBM Plex Sans"),
};
