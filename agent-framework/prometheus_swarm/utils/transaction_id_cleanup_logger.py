import logging
import os
from typing import Optional, Union

class TransactionIdCleanupLogger:
    """
    A specialized logger for tracking transaction ID cleanup operations.
    
    This logger provides structured logging for transaction ID cleanup processes,
    capturing important events, errors, and metrics during cleanup operations.
    """
    
    def __init__(self, log_level: int = logging.INFO, log_dir: Optional[str] = None):
        """
        Initialize the TransactionIdCleanupLogger.
        
        Args:
            log_level (int): Logging level (default: logging.INFO)
            log_dir (str, optional): Directory to store log files. 
                                     If None, uses a default logs directory.
        """
        self.logger = logging.getLogger('transaction_id_cleanup')
        self.logger.setLevel(log_level)
        
        # Configure log directory
        if log_dir is None:
            log_dir = os.path.join(os.getcwd(), 'logs', 'transaction_cleanup')
        
        # Ensure full path is created
        os.makedirs(log_dir, exist_ok=True)
        
        # File handler
        log_file = os.path.join(log_dir, 'transaction_id_cleanup.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # Log format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log_cleanup_start(self, transaction_id: str):
        """
        Log the start of a transaction ID cleanup operation.
        
        Args:
            transaction_id (str): The transaction ID being cleaned up
        """
        self.logger.info(f"Starting cleanup for transaction ID: {transaction_id}")
    
    def log_cleanup_success(
        self, 
        transaction_id: str, 
        num_records_deleted: int, 
        cleanup_duration: float
    ):
        """
        Log a successful transaction ID cleanup operation.
        
        Args:
            transaction_id (str): The transaction ID that was cleaned up
            num_records_deleted (int): Number of records deleted
            cleanup_duration (float): Time taken for cleanup in seconds
        """
        self.logger.info(
            f"Cleanup successful for transaction ID: {transaction_id}. "
            f"Records deleted: {num_records_deleted}. "
            f"Duration: {cleanup_duration:.4f} seconds"
        )
    
    def log_cleanup_error(
        self, 
        transaction_id: str, 
        error: Union[Exception, str]
    ):
        """
        Log an error during transaction ID cleanup.
        
        Args:
            transaction_id (str): The transaction ID that failed cleanup
            error (Exception or str): The error that occurred
        """
        self.logger.error(
            f"Cleanup failed for transaction ID: {transaction_id}. "
            f"Error: {str(error)}"
        )
    
    def log_cleanup_skipped(
        self, 
        transaction_id: str, 
        reason: str
    ):
        """
        Log when a transaction ID cleanup is skipped.
        
        Args:
            transaction_id (str): The transaction ID skipped
            reason (str): Reason for skipping the cleanup
        """
        self.logger.warning(
            f"Cleanup skipped for transaction ID: {transaction_id}. "
            f"Reason: {reason}"
        )