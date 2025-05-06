import logging
from typing import Any, Dict, Optional
from datetime import datetime, timezone
import json
import os

class SignatureLogger:
    """
    A utility class for logging and monitoring signatures with comprehensive tracking.
    """
    
    def __init__(
        self, 
        log_dir: Optional[str] = None, 
        log_level: int = logging.INFO
    ):
        """
        Initialize the SignatureLogger.
        
        :param log_dir: Directory to store signature log files. Defaults to './signature_logs'
        :param log_level: Logging level, defaults to INFO
        """
        self.log_dir = log_dir or './signature_logs'
        self.log_level = log_level
        
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=self.log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('SignatureLogger')
    
    def log_signature(
        self, 
        signature: str, 
        metadata: Optional[Dict[str, Any]] = None, 
        category: str = 'default'
    ) -> None:
        """
        Log a signature with optional metadata.
        
        :param signature: The signature to log
        :param metadata: Additional context about the signature
        :param category: Categorization for the signature
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        log_entry = {
            'timestamp': timestamp,
            'signature': signature,
            'category': category,
            'metadata': metadata or {}
        }
        
        # Log to console with signature explicitly mentioned
        self.logger.info(f"Logging Signature: {signature} | Full Entry: {json.dumps(log_entry)}")
        
        # Log to file
        log_file_path = os.path.join(
            self.log_dir, 
            f'signatures_{datetime.now().strftime("%Y%m%d")}.log'
        )
        
        with open(log_file_path, 'a') as log_file:
            log_file.write(json.dumps(log_entry) + '\n')
    
    def monitor_signatures(
        self, 
        signatures: list[str], 
        threshold: int = 10
    ) -> Dict[str, int]:
        """
        Monitor signature frequencies and detect anomalies.
        
        :param signatures: List of signatures to monitor
        :param threshold: Maximum acceptable frequency
        :return: Dictionary of signature frequencies
        """
        signature_counts = {}
        
        for sig in signatures:
            log_file_path = os.path.join(
                self.log_dir, 
                f'signatures_{datetime.now().strftime("%Y%m%d")}.log'
            )
            
            if not os.path.exists(log_file_path):
                signature_counts[sig] = 0
                continue
            
            with open(log_file_path, 'r') as log_file:
                count = sum(
                    1 for line in log_file 
                    if sig in line
                )
                signature_counts[sig] = count
                
                if count > threshold:
                    self.logger.warning(
                        f"Signature {sig} exceeded threshold: {count} occurrences"
                    )
        
        return signature_counts