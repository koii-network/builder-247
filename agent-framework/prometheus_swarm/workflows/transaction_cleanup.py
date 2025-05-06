import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from prometheus_swarm.database.database import SessionLocal
from prometheus_swarm.database.models import TransactionLog  # Assuming this model exists

class TransactionCleanupJob:
    """
    Background job to clean up old transaction logs from the database.
    
    This job removes transaction logs that are older than a specified retention period.
    """
    
    @staticmethod
    def cleanup_old_transactions(
        retention_days: int = 30, 
        max_delete_batch: Optional[int] = 10000
    ) -> int:
        """
        Remove transaction logs older than the specified retention period.
        
        Args:
            retention_days (int): Number of days to retain transaction logs. Defaults to 30.
            max_delete_batch (Optional[int]): Maximum number of records to delete in one batch. 
                                             Defaults to 10000 to prevent overwhelming the database.
        
        Returns:
            int: Number of transaction logs deleted
        """
        try:
            # Create a database session
            db: Session = SessionLocal()
            
            # Calculate the cutoff date for deletion
            cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=retention_days)
            
            # Count and delete old transactions in batches
            deleted_count = 0
            while True:
                # Find and delete old transactions in batches
                old_transactions = (
                    db.query(TransactionLog)
                    .filter(TransactionLog.created_at < cutoff_date)
                    .limit(max_delete_batch)
                    .all()
                )
                
                # If no more old transactions, break the loop
                if not old_transactions:
                    break
                
                # Delete the batch of old transactions
                for transaction in old_transactions:
                    db.delete(transaction)
                
                # Commit the deletion batch
                db.commit()
                
                # Update the deletion count
                deleted_count += len(old_transactions)
                
                # If batch is less than max, we've processed all old transactions
                if len(old_transactions) < max_delete_batch:
                    break
            
            return deleted_count
        
        except Exception as e:
            # Log the error or handle it as appropriate for your application
            print(f"Error in transaction cleanup: {e}")
            return 0
        finally:
            # Always close the session
            db.close()