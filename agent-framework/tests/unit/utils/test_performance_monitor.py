import pytest
import time
from unittest.mock import patch, MagicMock

from prometheus_swarm.utils.performance_monitor import PerformanceMonitor, PerformanceMetrics

def test_performance_metrics_initialization():
    """Test PerformanceMetrics initialization."""
    metrics = PerformanceMetrics(
        cpu_percent=50.0,
        memory_percent=75.0,
        memory_used_mb=1024.0,
        memory_total_mb=2048.0
    )
    
    assert metrics.cpu_percent == 50.0
    assert metrics.memory_percent == 75.0
    assert metrics.memory_used_mb == 1024.0
    assert metrics.memory_total_mb == 2048.0
    assert metrics.disk_usage_percent is None
    assert metrics.network_sent_mb is None
    assert metrics.network_recv_mb is None

def test_performance_monitor_initialization():
    """Test PerformanceMonitor initialization."""
    monitor = PerformanceMonitor(log_interval=30)
    
    assert monitor._log_interval == 30
    assert monitor._monitoring_thread is None
    assert not monitor._stop_event.is_set()

@patch('psutil.cpu_percent')
@patch('psutil.virtual_memory')
@patch('psutil.disk_usage')
@patch('psutil.net_io_counters')
def test_get_performance_metrics(mock_net_io, mock_disk_usage, mock_vm, mock_cpu_percent):
    """Test getting performance metrics."""
    # Mock the return values
    mock_cpu_percent.return_value = 55.5
    mock_vm.return_value = MagicMock(
        percent=70.0, 
        used=1536 * 1024 * 1024,  # 1.5 GB
        total=2048 * 1024 * 1024  # 2 GB
    )
    mock_disk_usage.return_value = MagicMock(percent=80.0)
    mock_net_io.return_value = MagicMock(
        bytes_sent=1024 * 1024 * 100,  # 100 MB
        bytes_recv=1024 * 1024 * 200   # 200 MB
    )

    monitor = PerformanceMonitor()
    
    # First call will set initial network counters
    initial_metrics = monitor._get_performance_metrics()
    
    # Second call will compute network transfer
    time.sleep(1)  # Simulate time passing
    metrics = monitor._get_performance_metrics()

    assert metrics.cpu_percent == 55.5
    assert metrics.memory_percent == 70.0
    assert metrics.memory_used_mb == 1536.0
    assert metrics.memory_total_mb == 2048.0
    assert metrics.disk_usage_percent == 80.0

def test_callback_invocation():
    """Test callback is called with metrics."""
    callback_called = False
    def test_callback(metrics):
        nonlocal callback_called
        callback_called = True
        assert isinstance(metrics, dict)
    
    monitor = PerformanceMonitor(log_interval=0.1)
    monitor.start_monitoring(callback=test_callback)
    
    time.sleep(0.5)  # Give time for callback to be called
    monitor.stop_monitoring()
    
    assert callback_called

def test_start_stop_monitoring():
    """Test starting and stopping monitoring."""
    monitor = PerformanceMonitor(log_interval=0.1)
    
    monitor.start_monitoring()
    assert monitor._monitoring_thread is not None
    assert monitor._monitoring_thread.is_alive()
    
    monitor.stop_monitoring()
    assert not monitor._monitoring_thread.is_alive()

def test_current_metrics_retrieval():
    """Test getting current metrics."""
    monitor = PerformanceMonitor()
    metrics = monitor.get_current_metrics()
    
    assert isinstance(metrics, dict)
    required_keys = [
        'cpu_percent', 'memory_percent', 
        'memory_used_mb', 'memory_total_mb',
        'timestamp'
    ]
    
    for key in required_keys:
        assert key in metrics
        assert isinstance(metrics[key], (int, float))