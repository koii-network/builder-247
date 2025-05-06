import time
import logging
import pytest
from prometheus_swarm.utils.performance_monitor import PerformanceMonitor

def test_track_performance_decorator():
    @PerformanceMonitor.track_performance(warning_threshold=0.1)
    def slow_function():
        time.sleep(0.2)  # Simulate a slow operation
    
    with pytest.raises(logging.LogRecord):
        with pytest.caplog.at_level(logging.WARNING):
            slow_function()
            assert "Performance Warning" in pytest.caplog.text

def test_track_performance_fast_function():
    @PerformanceMonitor.track_performance(warning_threshold=1.0)
    def fast_function():
        time.sleep(0.05)  # Simulate a fast operation
    
    with pytest.caplog.at_level(logging.WARNING):
        fast_function()
        assert len(pytest.caplog.records) == 0

def test_log_performance():
    start_time = time.time()
    time.sleep(0.1)  # Simulate some operation
    
    metrics = PerformanceMonitor.log_performance(
        "test_operation", 
        start_time, 
        logger=logging.getLogger()
    )
    
    assert "test_operation" in metrics['operation']
    assert metrics['execution_time'] >= 0.1
    assert metrics['end_time'] > metrics['start_time']

def test_log_performance_with_custom_logger():
    custom_logger = logging.getLogger('test_logger')
    custom_logger.setLevel(logging.INFO)
    
    start_time = time.time()
    time.sleep(0.05)
    
    with pytest.caplog.at_level(logging.INFO, logger='test_logger'):
        metrics = PerformanceMonitor.log_performance(
            "custom_operation", 
            start_time, 
            logger=custom_logger
        )
        
        assert "custom_operation" in metrics['operation']
        assert "Performance Metrics" in pytest.caplog.text