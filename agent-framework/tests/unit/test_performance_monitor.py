import pytest
import time
from unittest.mock import Mock, patch
from prometheus_client import REGISTRY
from prometheus_swarm.utils.performance_monitor import PerformanceMonitor

def test_performance_monitor_initialization():
    """Test that the PerformanceMonitor initializes metrics correctly."""
    monitor = PerformanceMonitor()
    
    assert hasattr(monitor, 'job_duration')
    assert hasattr(monitor, 'job_total_count')
    assert hasattr(monitor, 'job_success_count')
    assert hasattr(monitor, 'job_failure_count')

def test_performance_monitor_decorator_success():
    """Test the performance monitor decorator for a successful job."""
    monitor = PerformanceMonitor()
    
    @monitor.monitor_job
    def successful_job(x, y):
        return x + y
    
    with patch('prometheus_swarm.utils.performance_monitor.logging.Logger.info') as mock_log:
        result = successful_job(3, 4)
        
        assert result == 7
        assert mock_log.called
        assert 'completed successfully' in mock_log.call_args[0][0]

def test_performance_monitor_decorator_failure():
    """Test the performance monitor decorator for a failed job."""
    monitor = PerformanceMonitor()
    
    @monitor.monitor_job
    def failing_job():
        raise ValueError("Test failure")
    
    with patch('prometheus_swarm.utils.performance_monitor.logging.Logger.error') as mock_log:
        with pytest.raises(ValueError, match="Test failure"):
            failing_job()
        
        assert mock_log.called
        assert 'failed' in mock_log.call_args[0][0]

def test_performance_monitor_metrics_increment():
    """Test that metrics are incremented correctly."""
    monitor = PerformanceMonitor()
    
    @monitor.monitor_job
    def sample_job():
        time.sleep(0.1)  # Simulate some work
        return True
    
    # Capture initial metric values
    total_count_before = REGISTRY.get_sample_value('cleanup_job_job_total_count')
    success_count_before = REGISTRY.get_sample_value('cleanup_job_job_success_count')
    
    sample_job()
    
    # Check metric increments
    total_count_after = REGISTRY.get_sample_value('cleanup_job_job_total_count')
    success_count_after = REGISTRY.get_sample_value('cleanup_job_job_success_count')
    
    assert total_count_after == total_count_before + 1
    assert success_count_after == success_count_before + 1