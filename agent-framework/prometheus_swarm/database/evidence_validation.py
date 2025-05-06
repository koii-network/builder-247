from typing import Any, Dict, List
from .database import get_db

def validate_evidence_uniqueness(evidence: Dict[str, Any], table_name: str = 'evidence') -> bool:
    """
    Validate that an evidence entry is unique across the specified table.
    
    Args:
        evidence (Dict[str, Any]): The evidence dictionary to validate
        table_name (str, optional): The database table to check against. Defaults to 'evidence'.
    
    Returns:
        bool: True if the evidence is unique, False otherwise
    
    Raises:
        ValueError: If the evidence is invalid or missing key fields
    """
    if not evidence:
        raise ValueError("Evidence cannot be empty")
    
    # Define fields that must be unique
    unique_fields = ['hash', 'source', 'type']
    
    # Validate presence of unique fields
    for field in unique_fields:
        if field not in evidence:
            raise ValueError(f"Missing required unique field: {field}")
    
    try:
        # Get database session
        db = get_db()
        
        # Construct query to check uniqueness
        query = f"SELECT COUNT(*) as count FROM {table_name} WHERE "
        conditions = [f"{field} = :{field}" for field in unique_fields]
        query += " AND ".join(conditions)
        
        # Execute query
        result = db.execute(query, evidence).scalar()
        
        # If count is 0, the evidence is unique
        return result == 0
    
    except Exception as e:
        # Log the error in a real-world scenario
        raise ValueError(f"Error validating evidence uniqueness: {e}")
    finally:
        if 'db' in locals():
            db.close()