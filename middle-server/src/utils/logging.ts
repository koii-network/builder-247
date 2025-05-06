// Simplified logging utility
export class Logger {
  static info(message: string, meta?: Record<string, any>) {
    console.info(JSON.stringify({ message, ...meta }));
  }

  static warn(message: string, meta?: Record<string, any>) {
    console.warn(JSON.stringify({ message, ...meta }));
  }

  static error(message: string, meta?: Record<string, any>) {
    console.error(JSON.stringify({ message, ...meta }));
  }
}