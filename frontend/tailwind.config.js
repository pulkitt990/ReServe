/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        reserve: {
          dark: '#1B4332',      // Deep confident forest green anchor
          primary: '#2D6A4F',   // Ripe leaf green
          light: '#52B788',     // Fresh stem green
          surface: '#F4F6F0',   // Natural harvest linen near-white
          urgency: '#E8A33D',   // Warm ripe mango/marigold for urgent states/CTAs
          critical: '#C0392B',  // High-perishability alert red
          muted: '#6C757D',     // Subtle slate
        }
      },
      fontFamily: {
        display: ['Fraunces', 'Georgia', 'serif'],
        sans: ['Plus Jakarta Sans', 'Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
