"""Shared database configuration."""

import os
from pathlib import Path
from sqlalchemy import create_engine
from typing import Optional, Union

class TransactionIDRetentionConfig:
    """Configuration for Transaction ID retention."""

    def __init__(
        self, 
        max_retention_days: Optional[int] = None, 
        max_retention_count: Optional[int] = None, 
        enable_pruning: Optional[bool] = None
    ):
        """
        Initialize Transaction ID retention configuration.

        Precedence:
        1. Explicitly passed arguments
        2. Environment variables
        3. Default values

        Args:
            max_retention_days (int, optional): Maximum number of days to keep transaction IDs.
            max_retention_count (int, optional): Maximum number of transaction IDs to retain.
            enable_pruning (bool, optional): Enable automatic pruning of old transaction IDs.
        """
        # Environment variable parsing with type conversion and error handling
        env_retention_days = os.getenv('TRANSACTION_ID_MAX_RETENTION_DAYS')
        env_retention_count = os.getenv('TRANSACTION_ID_MAX_RETENTION_COUNT')
        env_enable_pruning = os.getenv('TRANSACTION_ID_ENABLE_PRUNING')

        # Priority to passed arguments, then environment variables, then default values
        self.max_retention_days = (
            max_retention_days if max_retention_days is not None 
            else int(env_retention_days) if env_retention_days is not None and env_retention_days.isdigit()
            else 30
        )
        
        self.max_retention_count = (
            max_retention_count if max_retention_count is not None
            else int(env_retention_count) if env_retention_count is not None and env_retention_count.isdigit()
            else 1000
        )
        
        self.enable_pruning = (
            enable_pruning if enable_pruning is not None
            else env_enable_pruning.lower() == 'true' if env_enable_pruning is not None
            else True
        )

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