/**
 * Design Tokens - Colors
 * BTS Global Corp Design System
 * 
 * Adaptado para React/TypeScript do BTS Design System
 * Princípios visuais: Sofisticado, moderno, confiável
 * Paleta sóbria (azul escuro, branco, preto, toques de azul-claro)
 */

export const colors = {
  // ============================================
  // PRIMARY BRAND COLORS
  // ============================================

  primary: {
    white: '#FFFFFF',           // C0 M0 Y0 K0 | R255 G255 B255
    black: '#000000',           // C0 M0 Y0 K100 | R0 G0 B0
    blue: '#1B3857',            // C88 M65 Y0 K78 | R18 G37 E87
    blueHighlight: '#1B5AB4',   // C87 M50 Y0 K29 | R27 G90 B180
  },

  // ============================================
  // SECONDARY BRAND COLORS
  // ============================================

  secondary: {
    blueC01: '#1B3857',         // C74 M61 Y0 K64 | R46 G54 B91
    blueC02: '#1B4668',         // C100 M33 Y0 K42 | R0 G99 B147
    blue503: '#0C80A5',         // C100 M34 Y0 K35 | R0 G108 B165
    blueC04: '#2A7BA1',         // C78 M25 Y0 K37 | R46 G123 B161
    blue505: '#63C9F3',         // C61 M26 Y0 K5 | R68 G181 B243
    gray506: '#B2B2B2',         // C0 M0 Y0 K9 | R232 G232 B232
  },

  // ============================================
  // NEUTRAL COLORS
  // ============================================

  neutral: {
    white: '#FFFFFF',           // C0 M0 Y0 K0 | R255 G255 B255
    grayLight: '#E4E4E4',       // C3 M4 Y0 K5 | R229 G229 B244
    graySemiLight: '#C9C9C9',   // C12 M8 Y9 K10 | R229 G229 B229
    grayBase: '#C6C6C6',        // C0 M0 Y0 K25 | R198 G198 B198
    graySemiDark: '#9B9B9B',    // C42 M33 Y33 K10 | R149 G149 B149
    grayDark: '#595757',        // C60 M50 Y48 K42 | R87 G87 B87
    black: '#333333',           // C0 M0 Y0 K90 | R19 G19 B19
  },

  // ============================================
  // FEEDBACK COLORS
  // ============================================

  feedback: {
    success: {
      light: '#B1D2B1',
      semiLight: '#8CC28C',
      base: '#2E8B2E',
      semiDark: '#1A661A',
      dark: '#0D330D',
      darker: '#073307',
    },
    warning: {
      light: '#FFF4D1',
      semiLight: '#FFE6A4',
      base: '#FFD700',
      semiDark: '#B39600',
      dark: '#665500',
      darker: '#332B00',
    },
    error: {
      light: '#F9B6B6',
      semiLight: '#F48C8C',
      base: '#E63939',
      semiDark: '#A32929',
      dark: '#5C1717',
      darker: '#2E0C0C',
    },
    info: {
      light: '#63C9F3',
      semiLight: '#2A7BA1',
      base: '#0C80A5',
      semiDark: '#1B4668',
      dark: '#1B3857',
      darker: '#1B3857',
    },
  },

  // ============================================
  // TEXT COLORS
  // ============================================

  text: {
    primary: '#000000',
    secondary: '#333333',
    tertiary: '#595757',
    disabled: '#9B9B9B',
    inverse: '#FFFFFF',
    link: '#1B5AB4',
    linkHover: '#1B3857',
  },

  // ============================================
  // BACKGROUND COLORS
  // ============================================

  background: {
    default: '#FFFFFF',
    paper: '#E4E4E4',
    elevated: '#FFFFFF',
    dark: '#1B3857',
    light: '#C9C9C9',
    accent: '#63C9F3',
  },

  // ============================================
  // BORDER COLORS
  // ============================================

  border: {
    default: '#C6C6C6',
    light: '#E4E4E4',
    dark: '#9B9B9B',
    focus: '#1B5AB4',
    divider: '#B2B2B2',
  },
} as const;

export default colors;
