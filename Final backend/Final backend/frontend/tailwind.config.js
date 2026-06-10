const defaultTheme = require('tailwindcss/defaultTheme');

/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './pages/**/*.{js,jsx}',
    './components/**/*.{js,jsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', ...defaultTheme.fontFamily.sans],
      },
      colors: {
        brand: {
          50: '#ecfeff',
          100: '#cffafe',
          200: '#a5f3fc',
          300: '#67e8f9',
          400: '#22d3ee',
          500: '#06b6d4',
          600: '#0891b2',
          700: '#0e7490',
          800: '#155e75',
          900: '#164e63',
        },
        accent: {
          50: '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#4c1d95',
        },
        surface: {
          50: '#1e293b',
          100: '#1a1f2e',
          200: '#161a26',
          300: '#12141f',
          400: '#0f1119',
          500: '#0c0e15',
          600: '#0a0c12',
          700: '#08090e',
          800: '#06070a',
          900: '#040506',
        },
        dark: {
          50: '#18181b',
          100: '#151518',
          200: '#121215',
          300: '#0f0f12',
          400: '#0c0c0f',
          500: '#0a0a0f',
          600: '#080810',
          700: '#06060a',
          800: '#040408',
          900: '#020205',
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out forwards',
        'slide-up': 'slideUp 0.6s ease-out forwards',
        'pulse-glow': 'pulse-glow 3s ease-in-out infinite',
        'shimmer': 'shimmer 1.8s ease-in-out infinite',
        'float': 'float 4s ease-in-out infinite',
        'glow-border-spin': 'glow-border-spin 4s linear infinite',
        'live-pulse': 'live-pulse 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          from: { opacity: '0', transform: 'translateY(12px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        'pulse-glow': {
          '0%, 100%': {
            boxShadow: '0 0 8px rgba(6,182,212,0.15), 0 0 20px rgba(139,92,246,0.08)',
          },
          '50%': {
            boxShadow: '0 0 16px rgba(6,182,212,0.3), 0 0 40px rgba(139,92,246,0.15)',
          },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-6px)' },
        },
        'glow-border-spin': {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
        'live-pulse': {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 0 0 rgba(34,197,94,0.6)' },
          '50%': { opacity: '0.8', boxShadow: '0 0 0 6px rgba(34,197,94,0)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
};