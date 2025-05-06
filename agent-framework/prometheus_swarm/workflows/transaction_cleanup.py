"""
Transaction ID Cleanup Background Job Module

This module provides a background job to clean up old transaction IDs,
helping to manage database storage and improve performance.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List

from prometheus_swarm.database.database import SessionLocal
from prometheus_swarm.database.models import Transaction  # Assuming such a model exists

class TransactionCleanupJob:
    def __init__(self, 
                 retention_days: int = 30, 
                 max_delete_batch: int = 1000):
        """
        Initialize Transaction Cleanup Job

        Args:
            retention_days (int): Number of days to retain transaction records. 
                                  Defaults to 30 days.
            max_delete_batch (int): Maximum number of records to delete in one batch.
                                    Defaults to 1000.
        """
        self.retention_days = retention_days
        self.max_delete_batch = max_delete_batch
        self.logger = logging.getLogger(__name__)

    def clean_old_transactions(self) -> int:
        """
        Delete transactions older than the retention period.

        Returns:
            int: Number of transactions deleted
        """
        try:
            with SessionLocal() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
                
                # Query for old transactions
                old_transactions = (
                    session.query(Transaction)
                    .filter(Transaction.created_at < cutoff_date)
                    .limit(self.max_delete_batch)
                    .all()
                )

                # Delete old transactions
                delete_count = len(old_transactions)
                for transaction in old_transactions:
                    session.delete(transaction)
                
                session.commit()
                
                self.logger.info(f"Deleted {delete_count} old transactions")
                return delete_count

        except Exception as e:
            self.logger.error(f"Error in transaction cleanup: {e}")
            raise

def run_transaction_cleanup(
    retention_days: Optional[int] = None, 
    max_delete_batch: Optional[int] = None
) -> int:
    """
    Entry point for running transaction cleanup job.

    Args:
        retention_days (Optional[int]): Custom retention days. Uses default if not provided.
        max_delete_batch (Optional[int]): Custom max delete batch. Uses default if not provided.

    Returns:
        int: Number of transactions deleted
    """
    cleanup_job = TransactionCleanupJob(
        retention_days=retention_days or 30,
        max_delete_batch=max_delete_batch or 1000
    )
    return cleanup_job.clean_old_transactions()