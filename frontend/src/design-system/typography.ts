/**
 * Design Tokens - Typography
 * BTS Global Corp Design System
 * 
 * Adaptado para React/TypeScript do BTS Design System
 * Tipografia: Montserrat
 * Características: Clean, legível, modular
 * Princípios: Clara, direta e elegante
 */

export const typography = {
  // ============================================
  // FONT FAMILIES
  // ============================================

  fontFamily: {
    primary: '"Montserrat", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    secondary: '"Montserrat", sans-serif',
    mono: '"Fira Code", "Courier New", Courier, monospace',
  },

  // ============================================
  // FONT SIZES
  // ============================================

  fontSize: {
    xs: '0.75rem',      // 12px
    sm: '0.875rem',     // 14px
    base: '1rem',       // 16px - Body (Regular, 16px)
    lg: '1.125rem',     // 18px - Subtitle (Medium, 18px)
    xl: '1.25rem',      // 20px
    '2xl': '1.5rem',    // 24px - Heading 2 (Semibold, 24px)
    '3xl': '1.75rem',   // 28px - Heading 1 (Semibold, 28px)
    '4xl': '2.5rem',    // 40px - Display Medium (Medium, 40px)
    '5xl': '3.25rem',   // 52px - Display Large (Bold, 52px)
    caption: '0.5625rem',   // 9px - Caption (Medium, 9px)
    body2: '0.6875rem',     // 11px - Body 2 (Regular, 11px)
  },

  // ============================================
  // FONT WEIGHTS
  // ============================================

  fontWeight: {
    thin: 100,
    extralight: 200,
    light: 300,
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
    black: 900,
  },

  // ============================================
  // LINE HEIGHTS
  // ============================================

  lineHeight: {
    none: 1,
    tight: 1.25,
    snug: 1.375,
    normal: 1.5,
    relaxed: 1.625,
    loose: 2,
  },

  // ============================================
  // LETTER SPACING
  // ============================================

  letterSpacing: {
    tighter: '-0.05em',
    tight: '-0.025em',
    normal: '0',
    wide: '0.025em',
    wider: '0.05em',
    widest: '0.1em',
  },

  // ============================================
  // TEXT STYLES - Estilos Pré-definidos BTS
  // ============================================

  styles: {
    displayLarge: {
      fontSize: '3.25rem',    // 52px
      fontWeight: 700,        // Bold
      lineHeight: 1.2,
      letterSpacing: '-0.025em',
    },
    displayMedium: {
      fontSize: '2.5rem',     // 40px
      fontWeight: 500,        // Medium
      lineHeight: 1.2,
      letterSpacing: '-0.015em',
    },
    heading1: {
      fontSize: '1.75rem',    // 28px
      fontWeight: 600,        // Semibold
      lineHeight: 1.3,
      letterSpacing: '0',
    },
    heading2: {
      fontSize: '1.5rem',     // 24px
      fontWeight: 600,        // Semibold
      lineHeight: 1.3,
      letterSpacing: '0',
    },
    subtitle: {
      fontSize: '1.125rem',   // 18px
      fontWeight: 500,        // Medium
      lineHeight: 1.5,
      letterSpacing: '0',
    },
    body: {
      fontSize: '1rem',       // 16px
      fontWeight: 400,        // Regular
      lineHeight: 1.5,
      letterSpacing: '0',
    },
    body2: {
      fontSize: '0.6875rem',  // 11px
      fontWeight: 400,        // Regular
      lineHeight: 1.5,
      letterSpacing: '0',
    },
    caption: {
      fontSize: '0.5625rem',  // 9px
      fontWeight: 500,        // Medium
      lineHeight: 1.4,
      letterSpacing: '0.025em',
    },
    button: {
      fontSize: '0.875rem',   // 14px
      fontWeight: 600,        // Semibold
      lineHeight: 1.5,
      letterSpacing: '0.05em',
    },
  },
} as const;

export default typography;
