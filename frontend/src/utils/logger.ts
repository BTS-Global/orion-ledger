/**
 * Logger utility for structured logging in development and production
 * 
 * Usage:
 * - logger.dev() - Only shows in development mode
 * - logger.info() - Shows always, for informational messages
 * - logger.warn() - Shows always, for warnings
 * - logger.error() - Shows always, for errors
 */

const isDevelopment = import.meta.env?.DEV ?? true;

export const logger = {
  /**
   * Development-only logs
   * Only visible when running in development mode
   */
  dev: (...args: any[]) => {
    if (isDevelopment) {
      console.log('[DEV]', ...args);
    }
  },

  /**
   * Informational logs
   * Visible in all environments
   */
  info: (...args: any[]) => {
    console.info('[INFO]', ...args);
  },

  /**
   * Warning logs
   * Visible in all environments
   */
  warn: (...args: any[]) => {
    console.warn('[WARN]', ...args);
  },

  /**
   * Error logs
   * Visible in all environments
   */
  error: (...args: any[]) => {
    console.error('[ERROR]', ...args);
  },

  /**
   * Debug logs with context
   * Only visible in development
   */
  debug: (context: string, ...args: any[]) => {
    if (isDevelopment) {
      console.log(`[DEBUG:${context}]`, ...args);
    }
  },
};

export default logger;
