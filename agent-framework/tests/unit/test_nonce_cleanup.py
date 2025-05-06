import os
import time
import tempfile
import pytest
from prometheus_swarm.utils.nonce_cleanup import cleanup_expired_nonces, run_nonce_cleanup_job

def test_cleanup_expired_nonces():
    # Create a temporary directory for nonce files
    with tempfile.TemporaryDirectory() as temp_nonce_dir:
        # Create test nonce files with different modification times
        current_time = time.time()
        
        # Create an expired nonce file (modified 25 hours ago)
        expired_nonce_path = os.path.join(temp_nonce_dir, 'expired_nonce.txt')
        with open(expired_nonce_path, 'w') as f:
            f.write('expired nonce')
        os.utime(expired_nonce_path, (current_time - 25*3600, current_time - 25*3600))
        
        # Create a recent nonce file (modified 1 hour ago)
        recent_nonce_path = os.path.join(temp_nonce_dir, 'recent_nonce.txt')
        with open(recent_nonce_path, 'w') as f:
            f.write('recent nonce')
        os.utime(recent_nonce_path, (current_time - 1*3600, current_time - 1*3600))
        
        # Run cleanup
        result = cleanup_expired_nonces(temp_nonce_dir, expiration_hours=24)
        
        # Verify cleanup results
        assert 'expired_nonce.txt' in result['deleted']
        assert 'recent_nonce.txt' in result['remaining']
        assert len(result['deleted']) == 1
        assert len(result['remaining']) == 1
        assert not os.path.exists(expired_nonce_path)
        assert os.path.exists(recent_nonce_path)

def test_cleanup_nonexistent_directory():
    # Ensure no errors when trying to clean up a non-existent directory
    result = cleanup_expired_nonces('/path/to/nonexistent/directory')
    assert result == {"deleted": [], "remaining": []}

def test_run_nonce_cleanup_job():
    # Capture print statements to verify job runs
    import io
    import sys
    
    with tempfile.TemporaryDirectory() as temp_nonce_dir:
        # Redirect stdout to capture print
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # Run the cleanup job
        run_nonce_cleanup_job(temp_nonce_dir)
        
        # Reset stdout
        sys.stdout = sys.__stdout__
        
        # Check output contains expected log message
        assert "Nonce Cleanup Job" in captured_output.getvalue()