import datetime
from typing import List, Dict, Any, Optional, Callable, Type
from sqlmodel import SQLModel

def cleanup_expired_transactions(
    model_class: Optional[Type[SQLModel]] = None,
    expiration_column: str = 'created_at',
    expiration_threshold_hours: int = 24,
    max_batch_size: int = 1000,
    get_session: Optional[Callable] = None
) -> Dict[str, int]:
    """
    Clean up expired database records using a specified model.

    Args:
        model_class (Optional[Type[SQLModel]]): SQLModel class to clean up. 
        expiration_column (str): Column name used to determine record age.
        expiration_threshold_hours (int): Number of hours after which a record is considered expired.
        max_batch_size (int): Maximum number of records to delete in a single batch.
        get_session (Optional[Callable]): Optional custom session getter for dependency injection during testing.

    Returns:
        Dict[str, int]: A dictionary containing the number of deleted records.
    """
    from prometheus_swarm.database.database import get_database_session

    # Validate inputs
    if model_class is None:
        return {
            "status": "error", 
            "message": "No model class specified for cleanup",
            "deleted_transactions": 0
        }

    # Use provided session getter or default
    session_getter = get_session or get_database_session

    try:
        # Get a database session
        db_session = session_getter()

        # Calculate the expiration timestamp
        expiration_timestamp = datetime.datetime.utcnow() - datetime.timedelta(hours=expiration_threshold_hours)

        # Query expired records
        expired_records = (
            db_session.query(model_class)
            .filter(getattr(model_class, expiration_column) < expiration_timestamp)
            .limit(max_batch_size)
            .all()
        )

        # Count and delete expired records
        num_deleted = len(expired_records)
        
        for record in expired_records:
            db_session.delete(record)
        
        # Commit the changes
        db_session.commit()

        return {
            "status": "success",
            "deleted_transactions": num_deleted
        }

    except Exception as e:
        # Log the error and rollback the transaction
        if 'db_session' in locals():
            db_session.rollback()
        return {
            "status": "error",
            "message": str(e),
            "deleted_transactions": 0
        }
    finally:
        # Close the database session
        if 'db_session' in locals():
            db_session.close()