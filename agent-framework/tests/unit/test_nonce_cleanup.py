import os
import tempfile
import time
from datetime import datetime, timedelta
import pytest
from prometheus_swarm.utils.nonce_cleanup import NonceCleanupJob

def test_nonce_cleanup_job_initialization():
    """Test job initialization with default and custom max age."""
    default_job = NonceCleanupJob()
    custom_job = NonceCleanupJob(max_age_hours=12)
    
    assert default_job.max_age_hours == 24
    assert custom_job.max_age_hours == 12

def test_nonce_cleanup_empty_directory():
    """Test cleanup job behavior with an empty directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        job = NonceCleanupJob()
        result = job.cleanup_nonces(temp_dir)
        
        assert result['total_files'] == 0
        assert result['deleted_files'] == 0
        assert result['error_files'] == 0

def test_nonce_cleanup_file_deletion():
    """Test that files older than max age are deleted."""
    with tempfile.TemporaryDirectory() as temp_dir:
        job = NonceCleanupJob(max_age_hours=1)
        
        # Create old files
        old_file_path1 = os.path.join(temp_dir, 'old_nonce1.txt')
        old_file_path2 = os.path.join(temp_dir, 'old_nonce2.txt')
        
        with open(old_file_path1, 'w') as f:
            f.write('old nonce 1')
        with open(old_file_path2, 'w') as f:
            f.write('old nonce 2')
        
        # Set modification time to 2 hours ago
        two_hours_ago = datetime.now() - timedelta(hours=2)
        os.utime(old_file_path1, (two_hours_ago.timestamp(), two_hours_ago.timestamp()))
        os.utime(old_file_path2, (two_hours_ago.timestamp(), two_hours_ago.timestamp()))
        
        result = job.cleanup_nonces(temp_dir)
        
        assert result['total_files'] == 2
        assert result['deleted_files'] == 2
        assert result['error_files'] == 0
        
        # Verify files are deleted
        assert not os.path.exists(old_file_path1)
        assert not os.path.exists(old_file_path2)

def test_nonce_cleanup_job_run():
    """Test the full job run method."""
    with tempfile.TemporaryDirectory() as temp_dir:
        job = NonceCleanupJob(max_age_hours=1)
        
        # Simulate some files
        for i in range(5):
            file_path = os.path.join(temp_dir, f'nonce_{i}.txt')
            with open(file_path, 'w') as f:
                f.write(f'nonce content {i}')
        
        # Make some files old
        for i in range(3):
            old_file_path = os.path.join(temp_dir, f'nonce_{i}.txt')
            two_hours_ago = datetime.now() - timedelta(hours=2)
            os.utime(old_file_path, (two_hours_ago.timestamp(), two_hours_ago.timestamp()))
        
        result = job.run_job(temp_dir)
        
        assert result['total_files'] == 5
        assert result['deleted_files'] == 3
        assert result['error_files'] == 0
        assert 'execution_time_seconds' in result
        assert result['max_age_hours'] == 1