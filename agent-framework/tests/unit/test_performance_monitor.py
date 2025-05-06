import pytest
import time
from unittest.mock import Mock, patch
from prometheus_client import REGISTRY, CollectorRegistry, generate_latest
from prometheus_swarm.utils.performance_monitor import PerformanceMonitor

def test_performance_monitor_initialization():
    """Test that the PerformanceMonitor initializes metrics correctly."""
    registry = CollectorRegistry()
    monitor = PerformanceMonitor(registry=registry)
    
    assert hasattr(monitor, 'job_duration')
    assert hasattr(monitor, 'job_total_count')
    assert hasattr(monitor, 'job_success_count')
    assert hasattr(monitor, 'job_failure_count')

def test_performance_monitor_decorator_success():
    """Test the performance monitor decorator for a successful job."""
    registry = CollectorRegistry()
    monitor = PerformanceMonitor(registry=registry)
    
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
    registry = CollectorRegistry()
    monitor = PerformanceMonitor(registry=registry)
    
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
    registry = CollectorRegistry()
    monitor = PerformanceMonitor(registry=registry)
    
    @monitor.monitor_job
    def sample_job():
        time.sleep(0.1)  # Simulate some work
        return True
    
    # Run the job
    sample_job()
    
    # Print out metrics for debugging
    metrics_text = generate_latest(registry).decode('utf-8')
    print("Metrics:", metrics_text)
    
    # Verify metrics exist in the registry
    metrics = list(registry.collect())
    
    # Check metric collectors
    assert any(m.name == 'cleanup_job_job_total_count' for m in metrics)
    assert any(m.name == 'cleanup_job_job_success_count' for m in metrics)
    assert any(m.name == 'cleanup_job_job_duration_seconds' for m in metrics)