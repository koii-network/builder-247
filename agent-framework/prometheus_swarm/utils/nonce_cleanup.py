import os
import time
from typing import List, Dict
from datetime import datetime, timedelta

def cleanup_expired_nonces(nonce_dir: str, expiration_hours: int = 24) -> Dict[str, List[str]]:
    """
    Clean up expired nonce files from a specified directory.

    Args:
        nonce_dir (str): Directory containing nonce files
        expiration_hours (int, optional): Hours after which a nonce is considered expired. Defaults to 24.

    Returns:
        Dict[str, List[str]]: A dictionary with 'deleted' and 'remaining' nonce files
    """
    if not os.path.exists(nonce_dir):
        return {"deleted": [], "remaining": []}

    current_time = datetime.now()
    deleted_nonces = []
    remaining_nonces = []

    for filename in os.listdir(nonce_dir):
        file_path = os.path.join(nonce_dir, filename)
        
        try:
            # Check file modification time
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            time_diff = current_time - file_mod_time

            if time_diff > timedelta(hours=expiration_hours):
                # Delete expired nonce file
                os.remove(file_path)
                deleted_nonces.append(filename)
            else:
                remaining_nonces.append(filename)
        except Exception as e:
            # Log or handle any errors during nonce cleanup
            print(f"Error processing nonce file {filename}: {e}")

    return {
        "deleted": deleted_nonces,
        "remaining": remaining_nonces
    }

def run_nonce_cleanup_job(nonce_dir: str, expiration_hours: int = 24):
    """
    Background job to periodically clean up expired nonce files.

    Args:
        nonce_dir (str): Directory containing nonce files
        expiration_hours (int, optional): Hours after which a nonce is considered expired. Defaults to 24.
    """
    try:
        result = cleanup_expired_nonces(nonce_dir, expiration_hours)
        print(f"Nonce Cleanup Job: Deleted {len(result['deleted'])} files")
    except Exception as e:
        print(f"Nonce Cleanup Job Error: {e}")