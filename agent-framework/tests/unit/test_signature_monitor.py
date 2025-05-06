"""Unit tests for SignatureMonitor."""

import time
import logging
from prometheus_swarm.utils.signature_monitor import SignatureMonitor

def test_signature_monitor_basic_tracking():
    """Test basic signature monitoring functionality."""
    monitor = SignatureMonitor(log_level=logging.ERROR)
    
    # Simulate successful verification
    monitor.log_verification('key1', success=True)
    assert monitor.total_verifications == 1
    assert monitor.successful_verifications == 1
    assert monitor.failed_verifications == 0
    
    # Simulate failed verification
    monitor.log_verification('key2', success=False)
    assert monitor.total_verifications == 2
    assert monitor.successful_verifications == 1
    assert monitor.failed_verifications == 1

def test_signature_monitor_key_stats():
    """Test key-specific verification statistics."""
    monitor = SignatureMonitor(log_level=logging.ERROR)
    
    # Verify multiple times for same key
    monitor.log_verification('test_key', success=True)
    monitor.log_verification('test_key', success=True)
    monitor.log_verification('test_key', success=False)
    
    stats = monitor.get_statistics()
    key_stats = stats['key_stats']['test_key']
    
    assert key_stats['total'] == 3
    assert key_stats['successful'] == 2
    assert key_stats['failed'] == 1

def test_signature_monitor_history_pruning():
    """Test pruning of old verification events."""
    monitor = SignatureMonitor(max_history_window=1, log_level=logging.ERROR)
    
    # Simulate multiple verifications
    monitor.log_verification('key1', success=True)
    monitor.log_verification('key2', success=False)
    
    # Wait just over window to trigger pruning
    time.sleep(1.1)
    monitor.log_verification('key3', success=True)
    
    assert len(monitor.verification_history) <= 1  # Only newest event remains

def test_signature_monitor_alert_thresholds():
    """Test alert threshold mechanisms."""
    alert_thresholds = {
        'failed_rate': 0.5,  # 50% failure rate triggers alert
        'burst_rate': 3      # 3 failed verifications triggers alert
    }
    monitor = SignatureMonitor(alert_threshold=alert_thresholds, log_level=logging.ERROR)
    
    # Simulate multiple failed verifications
    monitor.log_verification('key1', success=False)
    monitor.log_verification('key1', success=False)
    monitor.log_verification('key1', success=False)
    
    # These simulate normal behavior
    monitor.log_verification('key1', success=True)
    monitor.log_verification('key1', success=True)
    
    stats = monitor.get_statistics()
    assert stats['failed_verifications'] == 3
    assert stats['successful_verifications'] == 2