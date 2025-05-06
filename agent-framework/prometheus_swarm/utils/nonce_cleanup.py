import datetime
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func

def cleanup_expired_nonces(db: Session, max_age_hours: int = 24) -> int:
    """
    Clean up expired nonces from the database.

    Args:
        db (Session): SQLAlchemy database session
        max_age_hours (int): Maximum age of nonces in hours before they are considered expired

    Returns:
        int: Number of nonces deleted
    """
    if max_age_hours <= 0:
        raise ValueError("Max age must be a positive number")

    # Calculate the cutoff time for nonce expiration
    cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(hours=max_age_hours)

    try:
        # Delete nonces older than the cutoff time
        deleted_count = db.query(Nonce).filter(Nonce.created_at < cutoff_time).delete()
        db.commit()
        return deleted_count
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Failed to cleanup nonces: {str(e)}")