import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class ReplayAttackLogger:
    """
    A service for logging and detecting potential replay attacks.
    
    This class provides methods to:
    - Log unique request details
    - Check for potential replay attacks by tracking request signatures
    - Manage a log of requests with configurable storage
    """
    
    def __init__(self, log_dir: str = 'replay_attack_logs', max_log_entries: int = 1000):
        """
        Initialize the Replay Attack Logger.
        
        Args:
            log_dir (str): Directory to store log files. Defaults to 'replay_attack_logs'.
            max_log_entries (int): Maximum number of log entries to keep. Defaults to 1000.
        """
        self.log_dir = log_dir
        self.max_log_entries = max_log_entries
        
        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)
    
    def _generate_log_path(self, timestamp: Optional[datetime] = None) -> str:
        """
        Generate a log file path based on current or provided timestamp.
        
        Args:
            timestamp (datetime, optional): Timestamp to use for log file. Defaults to current time.
        
        Returns:
            str: Path to the log file
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        filename = f"replay_log_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        return os.path.join(self.log_dir, filename)
    
    def log_request(self, request_signature: str, request_details: Dict[str, Any]) -> bool:
        """
        Log a request and check for potential replay attacks.
        
        Args:
            request_signature (str): A unique identifier for the request
            request_details (Dict[str, Any]): Details of the request to log
        
        Returns:
            bool: False if request looks like a replay attack, True otherwise
        """
        # Validate inputs
        if not request_signature or not isinstance(request_details, dict):
            raise ValueError("Invalid request signature or details")
        
        # Check if this request signature has been seen before
        existing_log_files = sorted([f for f in os.listdir(self.log_dir) if f.startswith('replay_log_')])
        
        for log_file in existing_log_files[-self.max_log_entries:]:
            try:
                with open(os.path.join(self.log_dir, log_file), 'r') as f:
                    existing_logs = json.load(f)
                    
                    # Check if signature already exists
                    if any(log.get('request_signature') == request_signature for log in existing_logs):
                        return False  # Potential replay attack detected
            except (json.JSONDecodeError, IOError):
                # Handle potential file read/parse errors
                continue
        
        # Log the request
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'request_signature': request_signature,
            'request_details': request_details
        }
        
        log_path = self._generate_log_path()
        
        try:
            # Read existing logs or create new list
            existing_logs = []
            if os.path.exists(log_path):
                with open(log_path, 'r') as f:
                    existing_logs = json.load(f)
            
            # Add new log entry
            existing_logs.append(log_entry)
            
            # Trim logs if exceeding max entries
            existing_logs = existing_logs[-self.max_log_entries:]
            
            # Write back to file
            with open(log_path, 'w') as f:
                json.dump(existing_logs, f, indent=2)
            
            return True
        
        except IOError:
            # Handle file write errors
            return False