import os
import tempfile
import time
from prometheus_swarm.utils.nonce_cleanup import NonceCleanupJob

def test_nonce_cleanup_performance():
    """
    Test nonce cleanup performance for large number of entries.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create 100,000 nonce files
        for i in range(100_000):
            file_path = os.path.join(temp_dir, f'nonce_{i}.txt')
            with open(file_path, 'w') as f:
                f.write(f'nonce content {i}')
        
        job = NonceCleanupJob(max_age_hours=1)
        
        start_time = time.time()
        result = job.run_job(temp_dir)
        end_time = time.time()
        
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        print(f"Cleanup Performance: {execution_time} ms")
        print(f"Cleanup Result: {result}")
        
        assert execution_time < 500, f"Cleanup took too long: {execution_time} ms"
        assert result['total_files'] == 100_000
        assert result['execution_time_seconds'] is not None