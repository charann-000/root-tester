/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#0D1117',
        foreground: '#E6EDF3',
        card: '#161B22',
        border: '#30363D',
        accent: '#58A6FF',
        'accent-hover': '#79B8FF',
        destruct: '#F85149',
        'destruct-hover': '#FF6B6B',
        success: '#3FB950',
        warning: '#D29922',
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Consolas', 'Monaco', 'monospace'],
      },
    },
  },
  plugins: [],
}