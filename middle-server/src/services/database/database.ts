import mongoose from 'mongoose';
import dotenv from 'dotenv';

dotenv.config();

// Create separate connections for different databases
const mongoUri = process.env.MONGODB_URI || '';
const [baseUri, queryString] = mongoUri.split('?');
const options = queryString ? '?' + queryString : '';

// Remove any trailing slash from the base URI
const cleanBaseUri = baseUri.replace(/\/$/, '');

export const builder247DB = mongoose.createConnection(`${cleanBaseUri}/builder247${options}`);
export const prometheusDB = mongoose.createConnection(`${cleanBaseUri}/prometheus${options}`);

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
      new Promise<void>((resolve, reject) => {
        if (builder247DB.readyState === 1) {
          resolve();
        } else {
          builder247DB.once('connected', () => resolve());
          builder247DB.once('error', (err) => reject(err));
        }
      }),
      new Promise<void>((resolve, reject) => {
        if (prometheusDB.readyState === 1) {
          resolve();
        } else {
          prometheusDB.once('connected', () => resolve());
          prometheusDB.once('error', (err) => reject(err));
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

// Initialize connections
export const initializeConnections = async () => {
  try {
    await checkConnections();
    return true;
  } catch (error) {
    console.error('\x1b[31m%s\x1b[0m', 'Failed to initialize database connections:', error);
    return false;
  }
}; 


