import pytest
import time
from prometheus_swarm.utils.metrics import AgentMetrics

def test_agent_metrics_initialization():
    """Test metrics object can be created without errors."""
    metrics = AgentMetrics(metrics_port=8001)
    assert metrics is not None

def test_system_metrics_update():
    """Test system metrics can be updated."""
    metrics = AgentMetrics(metrics_port=8002)
    
    # Capture initial metrics
    metrics.update_system_metrics()
    
    # Verify metrics are recorded
    assert metrics.cpu_usage._value is not None
    assert metrics.memory_usage._value is not None
    assert metrics.disk_usage._value is not None

def test_task_tracking():
    """Test task tracking and timing."""
    metrics = AgentMetrics(metrics_port=8003)
    
    # Simulate a task
    with metrics.track_task():
        time.sleep(0.1)  # Simulate work
    
    # Check task was recorded
    assert metrics.task_counter._value.get() > 0

def test_error_recording():
    """Test error recording functionality."""
    metrics = AgentMetrics(metrics_port=8004)
    
    # Record different types of errors
    metrics.record_error("network")
    metrics.record_error("permission")
    
    # In a real scenario, we'd need to mock Prometheus client to precisely verify
    # For now, we just verify no exceptions are raised
    assert True

def test_periodic_update():
    """Test starting periodic updates."""
    metrics = AgentMetrics(metrics_port=8005)
    
    # Start updates in the background
    metrics.start_periodic_updates(interval=1)
    
    # Let it run for a short time
    time.sleep(2)
    
    # Verify metrics have been updated
    assert metrics.cpu_usage._value is not None