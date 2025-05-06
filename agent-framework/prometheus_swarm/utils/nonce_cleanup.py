import os
import time
from datetime import datetime, timedelta
from typing import Optional

class NonceCleanupJob:
    """
    Background job to clean up old nonce entries to prevent database bloat.
    """

    def __init__(self, max_age_hours: int = 24):
        """
        Initialize the Nonce Cleanup Job.
        
        Args:
            max_age_hours (int): Maximum age of nonces before deletion (default 24 hours)
        """
        self.max_age_hours = max_age_hours

    def cleanup_nonces(self, nonce_storage_path: str) -> dict:
        """
        Clean up nonces older than the specified max age.
        
        Args:
            nonce_storage_path (str): Path to the directory storing nonce files
        
        Returns:
            dict: Cleanup statistics
        """
        if not os.path.exists(nonce_storage_path):
            return {
                "total_files": 0,
                "deleted_files": 0,
                "error_files": 0
            }

        cleanup_stats = {
            "total_files": 0,
            "deleted_files": 0,
            "error_files": 0
        }

        try:
            # List all files in the nonce storage directory
            nonce_files = os.listdir(nonce_storage_path)
            cleanup_stats["total_files"] = len(nonce_files)

            current_time = datetime.now()
            max_age = timedelta(hours=self.max_age_hours)

            for filename in nonce_files:
                file_path = os.path.join(nonce_storage_path, filename)
                
                try:
                    # Get file's last modification time
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    # Check if file is older than max age
                    if current_time - file_mtime > max_age:
                        os.remove(file_path)
                        cleanup_stats["deleted_files"] += 1
                except Exception as e:
                    cleanup_stats["error_files"] += 1

        except Exception as e:
            # Log unexpected errors, but don't raise them to prevent job interruption
            print(f"Error in nonce cleanup: {e}")

        return cleanup_stats

    def run_job(self, nonce_storage_path: Optional[str] = None) -> dict:
        """
        Execute the nonce cleanup job.
        
        Args:
            nonce_storage_path (Optional[str]): Custom path to nonce storage. 
                If None, uses a default path.
        
        Returns:
            dict: Cleanup job results
        """
        if nonce_storage_path is None:
            # Default to a standard location if not specified
            nonce_storage_path = "/tmp/nonce_storage"
        
        # Ensure the directory exists
        os.makedirs(nonce_storage_path, exist_ok=True)
        
        # Measure job execution time
        start_time = time.time()
        cleanup_result = self.cleanup_nonces(nonce_storage_path)
        execution_time = time.time() - start_time
        
        # Enrich result with execution metadata
        cleanup_result.update({
            "execution_time_seconds": round(execution_time, 2),
            "max_age_hours": self.max_age_hours
        })
        
        return cleanup_result