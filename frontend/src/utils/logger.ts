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
   * Only visible in development, sent to monitoring in production
   */
  error: (message: string, error?: any) => {
    if (isDevelopment) {
      console.error('[ERROR]', message, error);
    } else {
      // In production, send to monitoring service (e.g., Sentry)
      // TODO: Integrate with Sentry or similar error tracking service
      // Sentry.captureException(error, { extra: { message } });
    }
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
