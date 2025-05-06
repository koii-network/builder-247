declare global {
  namespace Express {
    interface Request {
      transactionId?: string;
    }
  }
}

export {};