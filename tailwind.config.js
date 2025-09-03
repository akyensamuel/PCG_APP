/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./PCG_APP/templates/**/*.html",
    "./PCG_APP/**/templates/**/*.html",
    "./PCG_APP/**/views.py",
  ],
  theme: {
    extend: {
      colors: {
        // Presbyterian primary color only
        'pcg-blue': {
          DEFAULT: '#003366',
          600: '#00264d',
        }
      }
    },
  },
  plugins: [],
}
