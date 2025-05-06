import pytest
import time
from prometheus_swarm.utils.performance_monitor import PerformanceMonitor

def test_performance_track_decorator():
    """Test the performance tracking decorator."""
    
    @PerformanceMonitor.track_performance()
    def sample_function(x, y):
        time.sleep(0.1)  # Simulate some work
        return x + y
    
    # Test function works correctly
    result = sample_function(2, 3)
    assert result == 5

def test_performance_system_metrics():
    """Test system metrics retrieval."""
    
    metrics = PerformanceMonitor.get_system_metrics()
    
    # Check metrics structure and basic validation
    assert "cpu_percent" in metrics
    assert 0 <= metrics["cpu_percent"] <= 100
    
    assert "memory_usage" in metrics
    assert "total" in metrics["memory_usage"]
    assert "available" in metrics["memory_usage"]
    assert "percent" in metrics["memory_usage"]
    assert 0 <= metrics["memory_usage"]["percent"] <= 100
    
    assert "disk_usage" in metrics
    assert "total" in metrics["disk_usage"]
    assert "used" in metrics["disk_usage"]
    assert "percent" in metrics["disk_usage"]
    assert 0 <= metrics["disk_usage"]["percent"] <= 100

def test_performance_track_exception():
    """Test performance tracking with exception."""
    
    @PerformanceMonitor.track_performance()
    def error_function():
        raise ValueError("Test error")
    
    # Test that the decorator re-raises the original exception
    with pytest.raises(ValueError, match="Test error"):
        error_function()