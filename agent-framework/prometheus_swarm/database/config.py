"""Shared database configuration."""

import os
from pathlib import Path
from sqlalchemy import create_engine
from typing import Optional, Union

class TransactionIDRetentionConfig:
    """Configuration for Transaction ID retention."""

    def __init__(
        self, 
        max_retention_days: Optional[int] = 30, 
        max_retention_count: Optional[int] = 1000, 
        enable_pruning: bool = True
    ):
        """
        Initialize Transaction ID retention configuration.

        Args:
            max_retention_days (int, optional): Maximum number of days to keep transaction IDs. 
                Defaults to 30. None means no time-based limit.
            max_retention_count (int, optional): Maximum number of transaction IDs to retain. 
                Defaults to 1000. None means no count-based limit.
            enable_pruning (bool, optional): Enable automatic pruning of old transaction IDs. 
                Defaults to True.
        """
        self.max_retention_days = max_retention_days
        self.max_retention_count = max_retention_count
        self.enable_pruning = enable_pruning

    def validate(self) -> bool:
        """
        Validate the transaction ID retention configuration.

        Returns:
            bool: True if configuration is valid, False otherwise.
        """
        # Validate retention parameters
        if self.max_retention_days is not None and self.max_retention_days < 0:
            return False
        
        if self.max_retention_count is not None and self.max_retention_count < 0:
            return False
        
        return True

    def get_retention_limits(self) -> dict:
        """
        Get the current retention limits.

        Returns:
            dict: A dictionary containing retention configuration details.
        """
        return {
            "max_retention_days": self.max_retention_days,
            "max_retention_count": self.max_retention_count,
            "pruning_enabled": self.enable_pruning
        }

# Create engine
db_path = os.getenv("DATABASE_PATH", "sqlite:///database.db")
# If the path doesn't start with sqlite://, assume it's a file path and convert it
if not db_path.startswith("sqlite:"):
    path = Path(db_path).resolve()
    # Ensure the parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    # Convert to SQLite URL format with absolute path
    db_path = f"sqlite:///{path}"

engine = create_engine(db_path)