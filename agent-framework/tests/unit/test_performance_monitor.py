import time
import logging
import pytest
from prometheus_swarm.utils.performance_monitor import PerformanceMonitor

def test_track_performance_decorator(caplog):
    caplog.set_level(logging.WARNING)
    
    @PerformanceMonitor.track_performance(warning_threshold=0.1)
    def slow_function():
        time.sleep(0.2)  # Simulate a slow operation
    
    slow_function()
    assert "Performance Warning" in caplog.text

def test_track_performance_fast_function(caplog):
    caplog.set_level(logging.WARNING)
    
    @PerformanceMonitor.track_performance(warning_threshold=1.0)
    def fast_function():
        time.sleep(0.05)  # Simulate a fast operation
    
    fast_function()
    assert len(caplog.records) == 0

def test_log_performance(caplog):
    caplog.set_level(logging.INFO)
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
    assert "Performance Metrics" in caplog.text

def test_log_performance_with_custom_logger(caplog):
    custom_logger = logging.getLogger('test_logger')
    custom_logger.setLevel(logging.INFO)
    caplog.set_level(logging.INFO, logger='test_logger')
    
    start_time = time.time()
    time.sleep(0.05)
    
    metrics = PerformanceMonitor.log_performance(
        "custom_operation", 
        start_time, 
        logger=custom_logger
    )
    
    assert "custom_operation" in metrics['operation']
    assert "Performance Metrics" in caplog.text