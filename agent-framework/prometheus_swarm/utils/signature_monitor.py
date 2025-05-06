"""Signature Logging and Monitoring Module.

This module provides capabilities for logging and monitoring signature verification events,
tracking signature metrics, and detecting potential security issues.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

class SignatureMonitor:
    """
    A comprehensive signature monitoring system that tracks signature verification events.
    
    Tracks:
    - Total signature verifications
    - Successful and failed verification counts
    - Temporal signature verification patterns
    - Key-based verification statistics
    """
    
    def __init__(self, 
                 log_level: int = logging.INFO, 
                 max_history_window: int = 3600,  # 1 hour default window
                 alert_threshold: Dict[str, int] = None):
        """
        Initialize the SignatureMonitor.
        
        Args:
            log_level (int): Logging level for events
            max_history_window (int): Maximum time window to keep event history (seconds)
            alert_threshold (dict): Custom thresholds for different alert types
        """
        self.logger = logging.getLogger('signature_monitor')
        self.logger.setLevel(log_level)
        
        # Event tracking
        self.total_verifications = 0
        self.successful_verifications = 0
        self.failed_verifications = 0
        
        # Temporal tracking
        self.verification_history = []
        self.max_history_window = max_history_window
        
        # Key-based tracking
        self.key_verification_stats = defaultdict(lambda: {
            'total': 0,
            'successful': 0,
            'failed': 0
        })
        
        # Alert thresholds
        self.alert_threshold = alert_threshold or {
            'failed_rate': 0.1,  # 10% failure rate triggers alert
            'burst_rate': 10     # 10 failed verifications in short window
        }
    
    def log_verification(self, 
                         staking_key: str, 
                         success: bool, 
                         context: Optional[Dict[str, Any]] = None):
        """
        Log a signature verification event.
        
        Args:
            staking_key (str): Public key used for verification
            success (bool): Whether verification was successful
            context (dict, optional): Additional context about the verification
        """
        now = datetime.now()
        
        # Update total counts
        self.total_verifications += 1
        if success:
            self.successful_verifications += 1
        else:
            self.failed_verifications += 1
        
        # Update key-specific stats
        key_stats = self.key_verification_stats[staking_key]
        key_stats['total'] += 1
        key_stats['successful'] += 1 if success else 0
        key_stats['failed'] += 0 if success else 1
        
        # Record verification event
        event = {
            'timestamp': now,
            'staking_key': staking_key,
            'success': success,
            'context': context or {}
        }
        self.verification_history.append(event)
        
        # Prune old history
        self._prune_history()
        
        # Check for potential issues
        self._check_alerts(staking_key)
    
    def _prune_history(self):
        """Remove events older than max_history_window."""
        cutoff = datetime.now() - timedelta(seconds=self.max_history_window)
        self.verification_history = [
            event for event in self.verification_history 
            if event['timestamp'] > cutoff
        ]
    
    def _check_alerts(self, staking_key: str):
        """
        Check for potential security alerts based on verification patterns.
        
        Args:
            staking_key (str): Key to check for alerts
        """
        # Check overall failure rate
        if self.total_verifications > 0:
            failure_rate = self.failed_verifications / self.total_verifications
            if failure_rate > self.alert_threshold['failed_rate']:
                self.logger.warning(f"High signature verification failure rate: {failure_rate:.2%}")
        
        # Check verification burst for specific key
        key_recent_events = [
            event for event in self.verification_history 
            if event['staking_key'] == staking_key and not event['success']
        ]
        if len(key_recent_events) >= self.alert_threshold['burst_rate']:
            self.logger.error(f"Potential security issue: Multiple failed verifications for key {staking_key}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retrieve current signature verification statistics.
        
        Returns:
            dict: Comprehensive signature verification metrics
        """
        return {
            'total_verifications': self.total_verifications,
            'successful_verifications': self.successful_verifications,
            'failed_verifications': self.failed_verifications,
            'key_stats': dict(self.key_verification_stats)
        }

# Global singleton for easy import and use
signature_monitor = SignatureMonitor()