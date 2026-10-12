import type { Config } from 'tailwindcss'

export default {
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        obsidian: '#171615',
        graphite: '#282624',
        'graphite-light': '#342F2B',
        ivory: '#F5F0E8',
        'ivory-dim': '#C8C2B8',
        copper: '#B97853',
        'copper-light': '#D4966A',
        red: '#B84D43',
        'red-light': '#D4625A',
        sage: '#8EAA91',
        amber: '#D5A45B',
        border: '#3A3530',
        surface: '#1E1C1A',
      },
      fontFamily: {
        display: ['DM Serif Display', 'serif'],
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
} satisfies Config
