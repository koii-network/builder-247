import pytest
import time
from prometheus_swarm.performance_monitoring import PerformanceMonitor

def test_performance_monitor_record_metric():
    monitor = PerformanceMonitor()
    monitor.record_metric('test_metric', 1.5)
    
    metrics = monitor.get_metrics('test_metric')
    assert metrics['total_time'] == 1.5
    assert metrics['total_calls'] == 1
    assert metrics['min_time'] == 1.5
    assert metrics['max_time'] == 1.5

def test_performance_monitor_time_function():
    monitor = PerformanceMonitor()
    
    @monitor.time_function
    def slow_function(duration=0.1):
        time.sleep(duration)
        return "Done"
    
    result = slow_function()
    assert result == "Done"
    
    metrics = monitor.get_metrics('slow_function')
    assert metrics['total_calls'] == 1
    assert 0.09 < metrics['total_time'] < 0.11

def test_performance_monitor_context_manager():
    monitor = PerformanceMonitor()
    
    with monitor.track_performance('context_test'):
        time.sleep(0.2)
    
    metrics = monitor.get_metrics('context_test')
    assert metrics['total_calls'] == 1
    assert 0.19 < metrics['total_time'] < 0.21

def test_performance_monitor_multiple_metrics():
    monitor = PerformanceMonitor()
    
    @monitor.time_function
    def func1():
        time.sleep(0.1)
    
    @monitor.time_function
    def func2():
        time.sleep(0.2)
    
    func1()
    func2()
    
    func1_metrics = monitor.get_metrics('func1')
    func2_metrics = monitor.get_metrics('func2')
    
    assert func1_metrics['total_calls'] == 1
    assert func2_metrics['total_calls'] == 1
    assert 0.09 < func1_metrics['total_time'] < 0.11
    assert 0.19 < func2_metrics['total_time'] < 0.21

def test_performance_monitor_get_all_metrics():
    monitor = PerformanceMonitor()
    
    @monitor.time_function
    def func1():
        time.sleep(0.1)
    
    @monitor.time_function
    def func2():
        time.sleep(0.2)
    
    func1()
    func2()
    
    all_metrics = monitor.get_metrics()
    assert len(all_metrics) == 2
    assert 'func1' in all_metrics
    assert 'func2' in all_metrics