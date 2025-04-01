import mongoose from 'mongoose';
import dotenv from 'dotenv';

dotenv.config();

// Create separate connections for different databases
export const builder247DB = mongoose.createConnection(process.env.MONGODB_URI + '/builder247');
export const prometheusDB = mongoose.createConnection(process.env.MONGODB_URI + '/prometheus');

// Add connection event listeners
builder247DB.on('connected', () => {
  console.log('\x1b[32m%s\x1b[0m', 'Connected to builder247 database');
});

prometheusDB.on('connected', () => {
  console.log('\x1b[32m%s\x1b[0m', 'Connected to prometheus database');
});

builder247DB.on('error', (err) => {
  console.error('\x1b[31m%s\x1b[0m', 'builder247 database connection error:', err);
});

prometheusDB.on('error', (err) => {
  console.error('\x1b[31m%s\x1b[0m', 'prometheus database connection error:', err);
});

// Export a function to check connection status and wait for connections
export const checkConnections = async () => {
  try {
    // Wait for both connections to be ready
    await Promise.all([
      new Promise((resolve) => {
        if (builder247DB.readyState === 1) {
          resolve(true);
        } else {
          builder247DB.once('connected', () => resolve(true));
        }
      }),
      new Promise((resolve) => {
        if (prometheusDB.readyState === 1) {
          resolve(true);
        } else {
          prometheusDB.once('connected', () => resolve(true));
        }
      })
    ]);

    console.log('\x1b[32m%s\x1b[0m', 'Connected to all MongoDB databases');
    return true;
  } catch (error) {
    console.error('\x1b[31m%s\x1b[0m', 'Error checking database connections:', error);
    return false;
  }
}; 


