import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import os
import uuid

class NonceEventLogger:
    """
    A comprehensive logger for tracking nonce events with detailed logging and optional JSON output.
    
    Supports:
    - Logging nonce-related events
    - Configurable log levels
    - Optional JSON log file generation
    - Thread-safe logging
    """
    
    def __init__(
        self, 
        log_dir: Optional[str] = None, 
        log_level: int = logging.INFO, 
        enable_json_logs: bool = True
    ):
        """
        Initialize the NonceEventLogger.
        
        Args:
            log_dir (Optional[str]): Directory to store log files. Defaults to 'logs/nonce_events'.
            log_level (int): Logging level. Defaults to logging.INFO.
            enable_json_logs (bool): Whether to generate JSON log files. Defaults to True.
        """
        # Create log directory if it doesn't exist
        self.log_dir = log_dir or os.path.join('logs', 'nonce_events')
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Configure logging
        self.logger = logging.getLogger('nonce_event_logger')
        self.logger.setLevel(log_level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        self.enable_json_logs = enable_json_logs
    
    def log_nonce_event(
        self, 
        event_type: str, 
        details: Dict[str, Any], 
        severity: str = 'INFO'
    ) -> str:
        """
        Log a nonce-related event with optional JSON output.
        
        Args:
            event_type (str): Type of nonce event (e.g., 'generation', 'validation', 'collision')
            details (Dict[str, Any]): Event details and metadata
            severity (str): Event severity level. Defaults to 'INFO'
        
        Returns:
            str: Unique event identifier
        """
        # Generate unique event ID
        event_id = str(uuid.uuid4())
        
        # Prepare log entry
        log_entry = {
            'event_id': event_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type,
            'severity': severity,
            'details': details
        }
        
        # Log to console
        log_message = f"Nonce Event: {event_type} - {json.dumps(details)}"
        
        if severity.upper() == 'ERROR':
            self.logger.error(log_message)
        elif severity.upper() == 'WARNING':
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
        
        # Optional JSON logging
        if self.enable_json_logs:
            self._log_to_json(log_entry)
        
        return event_id
    
    def _log_to_json(self, log_entry: Dict[str, Any]):
        """
        Write log entry to a JSON file.
        
        Args:
            log_entry (Dict[str, Any]): Log entry to write
        """
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d')
        log_file_path = os.path.join(self.log_dir, f'nonce_events_{timestamp}.json')
        
        # Thread-safe JSON logging
        try:
            with open(log_file_path, 'a') as log_file:
                json.dump(log_entry, log_file)
                log_file.write('\n')  # Ensure each entry is on a new line
        except IOError as e:
            self.logger.error(f"Failed to write JSON log: {e}")