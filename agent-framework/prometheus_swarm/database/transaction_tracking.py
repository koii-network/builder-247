from typing import Dict, List, Optional
from datetime import datetime
import sqlite3
import os

def get_default_db_path():
    """
    Get the default database path.
    
    Creates the database directory if it doesn't exist.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(base_dir, 'data')
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, 'transactions.sqlite')

class TransactionTracker:
    """
    A data access layer for tracking transactions with comprehensive logging and error handling.
    
    Supports:
    - Recording transactions
    - Retrieving transactions
    - Searching transactions
    - Basic analytics
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the transaction tracker with a database connection.
        
        :param db_path: Optional custom database path. Uses default if not specified.
        """
        self.db_path = db_path or get_default_db_path()
        self._create_table()
    
    def _create_table(self):
        """
        Create the transactions table if it doesn't exist.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_type TEXT NOT NULL,
                    description TEXT,
                    amount REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            conn.commit()
    
    def record_transaction(
        self, 
        transaction_type: str, 
        description: str, 
        amount: float, 
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Record a new transaction.
        
        :param transaction_type: Type of transaction (e.g., 'deposit', 'withdrawal')
        :param description: Transaction description
        :param amount: Transaction amount
        :param metadata: Optional additional transaction details
        :return: Transaction ID
        """
        if not transaction_type or amount < 0:
            raise ValueError("Invalid transaction parameters")
        
        metadata_str = str(metadata) if metadata else None
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions 
                (transaction_type, description, amount, metadata) 
                VALUES (?, ?, ?, ?)
            ''', (transaction_type, description, amount, metadata_str))
            conn.commit()
            return cursor.lastrowid
    
    def get_transactions(
        self, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None, 
        transaction_type: Optional[str] = None, 
        limit: int = 100
    ) -> List[Dict]:
        """
        Retrieve transactions with optional filtering.
        
        :param start_date: Optional start date for transaction filtering
        :param end_date: Optional end date for transaction filtering
        :param transaction_type: Optional transaction type filter
        :param limit: Maximum number of transactions to return
        :return: List of transactions
        """
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        if transaction_type:
            query += " AND transaction_type = ?"
            params.append(transaction_type)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_total_amount(
        self, 
        transaction_type: Optional[str] = None, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> float:
        """
        Calculate total transaction amount with optional filtering.
        
        :param transaction_type: Optional transaction type filter
        :param start_date: Optional start date for calculation
        :param end_date: Optional end date for calculation
        :return: Total transaction amount
        """
        query = "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        if transaction_type:
            query += " AND transaction_type = ?"
            params.append(transaction_type)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()[0]