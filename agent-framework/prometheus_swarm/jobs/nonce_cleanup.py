import logging
from datetime import datetime, timedelta
from typing import List, Dict

class NonceCleanupJob:
    """
    Background job for cleaning up expired nonce tokens.
    
    This job removes nonce tokens that have exceeded their expiration time,
    helping to maintain security and manage resource usage.
    """
    
    def __init__(self, nonce_store: Dict[str, Dict], expiration_hours: int = 24):
        """
        Initialize the nonce cleanup job.
        
        :param nonce_store: Dictionary storing nonce tokens
        :param expiration_hours: Number of hours after which a nonce expires
        """
        self.nonce_store = nonce_store
        self.expiration_hours = expiration_hours
        self.logger = logging.getLogger(__name__)
    
    def find_expired_nonces(self) -> List[str]:
        """
        Find nonces that have expired based on the configured expiration time.
        
        :return: List of expired nonce keys to be removed
        """
        current_time = datetime.now()
        expired_nonces = []
        
        for nonce_key, nonce_data in self.nonce_store.items():
            # Check if nonce has a timestamp and has exceeded expiration
            if 'timestamp' in nonce_data:
                nonce_time = nonce_data['timestamp']
                if current_time - nonce_time > timedelta(hours=self.expiration_hours):
                    expired_nonces.append(nonce_key)
        
        return expired_nonces
    
    def cleanup(self) -> int:
        """
        Remove expired nonces from the store.
        
        :return: Number of nonces removed
        """
        expired_nonces = self.find_expired_nonces()
        
        for nonce_key in expired_nonces:
            del self.nonce_store[nonce_key]
            self.logger.info(f"Removed expired nonce: {nonce_key}")
        
        return len(expired_nonces)