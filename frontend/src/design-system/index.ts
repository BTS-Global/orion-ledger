/**
 * BTS Design System Tokens
 * Exportação centralizada de todos os design tokens
 */

export { colors, default as colorsDefault } from './colors';
export { typography, default as typographyDefault } from './typography';
export { spacing, shadows, borderRadius } from './spacing';

// Re-export tudo em um objeto único para conveniência
import colors from './colors';
import typography from './typography';
import { spacing, shadows, borderRadius } from './spacing';

export const tokens = {
  colors,
  typography,
  spacing,
  shadows,
  borderRadius,
};

export default tokens;
