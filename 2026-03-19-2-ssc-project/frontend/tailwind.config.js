/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#0d1f2d',
        ember: '#ff6b35',
        mint: '#2ec4b6',
        sand: '#f8f1e5'
      },
      boxShadow: {
        soft: '0 10px 30px rgba(0,0,0,0.12)'
      }
    }
  },
  plugins: []
};
