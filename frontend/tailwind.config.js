/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // BTS Design System - Font Family
      fontFamily: {
        sans: ['"Montserrat"', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', '"Helvetica Neue"', 'Arial', 'sans-serif'],
        mono: ['"Fira Code"', '"Courier New"', 'Courier', 'monospace'],
      },
      
      // BTS Design System - Colors
      colors: {
        // Primary Brand Colors
        'bts-blue': '#1B3857',
        'bts-blue-highlight': '#1B5AB4',
        'bts-white': '#FFFFFF',
        'bts-black': '#000000',
        
        // Secondary Colors
        'bts-blue-c01': '#1B3857',
        'bts-blue-c02': '#1B4668',
        'bts-blue-503': '#0C80A5',
        'bts-blue-c04': '#2A7BA1',
        'bts-blue-505': '#63C9F3',
        'bts-gray-506': '#B2B2B2',
        
        // Neutral Colors
        'bts-gray-light': '#E4E4E4',
        'bts-gray-semi-light': '#C9C9C9',
        'bts-gray-base': '#C6C6C6',
        'bts-gray-semi-dark': '#9B9B9B',
        'bts-gray-dark': '#595757',
        'bts-neutral-black': '#333333',
        
        // Feedback Colors
        'bts-success': '#2E8B2E',
        'bts-warning': '#FFD700',
        'bts-error': '#E63939',
        'bts-info': '#0C80A5',
        
        // Shadcn compatibility (mapped to BTS colors)
        background: '#FFFFFF',
        foreground: '#000000',
        card: {
          DEFAULT: '#FFFFFF',
          foreground: '#000000',
        },
        popover: {
          DEFAULT: '#FFFFFF',
          foreground: '#000000',
        },
        primary: {
          DEFAULT: '#1B5AB4',
          foreground: '#FFFFFF',
        },
        secondary: {
          DEFAULT: '#1B3857',
          foreground: '#FFFFFF',
        },
        muted: {
          DEFAULT: '#E4E4E4',
          foreground: '#595757',
        },
        accent: {
          DEFAULT: '#63C9F3',
          foreground: '#000000',
        },
        destructive: {
          DEFAULT: '#E63939',
          foreground: '#FFFFFF',
        },
        border: '#C6C6C6',
        input: '#C6C6C6',
        ring: '#1B5AB4',
        chart: {
          "1": '#1B5AB4',
          "2": '#0C80A5',
          "3": '#63C9F3',
          "4": '#2A7BA1',
          "5": '#1B4668',
        },
      },
      
      // BTS Design System - Border Radius
      borderRadius: {
        lg: '0.5rem',
        md: '0.375rem',
        sm: '0.25rem',
      },
      
      // BTS Design System - Shadows
      boxShadow: {
        sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        DEFAULT: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
