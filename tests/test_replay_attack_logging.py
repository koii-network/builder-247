import os
import pytest
import shutil
import time
from datetime import datetime
from src.replay_attack_logging import ReplayAttackLogger

class TestReplayAttackLogger:
    def setup_method(self):
        """Create a temporary log directory for each test"""
        self.test_log_dir = 'test_replay_attack_logs'
        os.makedirs(self.test_log_dir, exist_ok=True)
    
    def teardown_method(self):
        """Clean up the temporary log directory after each test"""
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
    
    def test_initialization(self):
        """Test logger initialization"""
        logger = ReplayAttackLogger(log_dir=self.test_log_dir)
        assert os.path.exists(self.test_log_dir)
    
    def test_log_request_success(self):
        """Test logging a unique request"""
        logger = ReplayAttackLogger(log_dir=self.test_log_dir)
        
        # First request should be logged successfully
        result = logger.log_request(
            request_signature='unique_request_1', 
            request_details={'user': 'test_user', 'action': 'login'}
        )
        assert result is True
        
        # Check log file was created
        log_files = os.listdir(self.test_log_dir)
        assert len(log_files) == 1
    
    def test_replay_attack_detection(self):
        """Test detecting a replay attack"""
        logger = ReplayAttackLogger(log_dir=self.test_log_dir)
        
        # First log of request
        first_log = logger.log_request(
            request_signature='duplicate_request', 
            request_details={'user': 'test_user', 'action': 'login'}
        )
        assert first_log is True
        
        # Second log with same signature should be rejected
        second_log = logger.log_request(
            request_signature='duplicate_request', 
            request_details={'user': 'test_user', 'action': 'login'}
        )
        assert second_log is False
    
    def test_max_log_entries(self):
        """Test that only max number of log entries are kept"""
        logger = ReplayAttackLogger(log_dir=self.test_log_dir, max_log_entries=3)
        
        # Log more than max_log_entries
        for i in range(5):
            result = logger.log_request(
                request_signature=f'request_{i}', 
                request_details={'user': f'user_{i}'}
            )
            assert result is True
            time.sleep(0.1)  # Ensure different timestamps
        
        # Check log files
        log_files = os.listdir(self.test_log_dir)
        assert len(log_files) == 1  # One log file
        
        # Read the log file and check entries
        import json
        with open(os.path.join(self.test_log_dir, log_files[0]), 'r') as f:
            logs = json.load(f)
        
        assert len(logs) == 3  # Only last 3 entries kept
        assert logs[0]['request_signature'] == 'request_2'
        assert logs[1]['request_signature'] == 'request_3'
        assert logs[2]['request_signature'] == 'request_4'
    
    def test_invalid_input(self):
        """Test handling of invalid inputs"""
        logger = ReplayAttackLogger(log_dir=self.test_log_dir)
        
        with pytest.raises(ValueError):
            logger.log_request('', {})
        
        with pytest.raises(ValueError):
            logger.log_request('test_sig', None)