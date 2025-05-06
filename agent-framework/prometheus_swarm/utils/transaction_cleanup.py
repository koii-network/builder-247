import datetime
from typing import List, Dict, Any, Optional, Callable
from contextlib import contextmanager

def cleanup_expired_transactions(
    expiration_threshold_hours: int = 24,
    max_batch_size: int = 1000,
    get_session: Optional[Callable] = None
) -> Dict[str, int]:
    """
    Clean up expired transactions from the database.

    Args:
        expiration_threshold_hours (int): Number of hours after which a transaction is considered expired.
        max_batch_size (int): Maximum number of transactions to delete in a single batch.
        get_session (Optional[Callable]): Optional custom session getter for dependency injection during testing.

    Returns:
        Dict[str, int]: A dictionary containing the number of deleted transactions.
    """
    from prometheus_swarm.database.database import get_database_session
    from prometheus_swarm.database.models import Transaction

    # Use provided session getter or default
    session_getter = get_session or get_database_session

    try:
        # Get a database session
        db_session = session_getter()

        # Calculate the expiration timestamp
        expiration_timestamp = datetime.datetime.utcnow() - datetime.timedelta(hours=expiration_threshold_hours)

        # Query expired transactions
        expired_transactions = (
            db_session.query(Transaction)
            .filter(Transaction.created_at < expiration_timestamp)
            .limit(max_batch_size)
            .all()
        )

        # Count and delete expired transactions
        num_deleted = len(expired_transactions)
        
        for transaction in expired_transactions:
            db_session.delete(transaction)
        
        # Commit the changes
        db_session.commit()

        return {
            "status": "success",
            "deleted_transactions": num_deleted
        }

    except Exception as e:
        # Log the error and rollback the transaction
        db_session.rollback()
        return {
            "status": "error",
            "message": str(e),
            "deleted_transactions": 0
        }
    finally:
        # Close the database session
        db_session.close()