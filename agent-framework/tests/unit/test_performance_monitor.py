import os
import time
import pytest
import logging
from prometheus_swarm.utils.performance_monitor import PerformanceMonitor

class TestPerformanceMonitor:
    @pytest.fixture
    def performance_monitor(self, tmp_path):
        log_path = os.path.join(tmp_path, 'performance_test.log')
        return PerformanceMonitor(log_path=log_path)

    def test_system_metrics(self, performance_monitor):
        """Test getting system metrics."""
        metrics = performance_monitor.get_system_metrics()
        
        assert isinstance(metrics, dict)
        assert 'cpu_percent' in metrics
        assert 'memory_percent' in metrics
        assert 0 <= metrics['cpu_percent'] <= 100
        assert 0 <= metrics['memory_percent'] <= 100

    def test_function_performance_tracking(self, performance_monitor):
        """Test function performance tracking decorator."""
        @performance_monitor.track_function()
        def sample_function(x, y):
            time.sleep(0.1)  # Simulate some work
            return x + y

        result = sample_function(2, 3)
        assert result == 5

    def test_function_performance_log(self, performance_monitor, caplog):
        """Test logging of function performance metrics."""
        caplog.set_level(logging.INFO)

        @performance_monitor.track_function()
        def complex_function():
            time.sleep(0.05)
            return sum(range(100))

        complex_function()

        # Check log contains key performance metrics
        log_records = [record for record in caplog.records if record.levelname == 'INFO']
        assert any('Performance Metrics' in record.message for record in log_records)
        assert any('execution_time_ms' in record.message for record in log_records)

    def test_exception_handling(self, performance_monitor, caplog):
        """Test performance tracking with exceptions."""
        caplog.set_level(logging.ERROR)

        @performance_monitor.track_function()
        def error_function():
            raise ValueError("Test Error")

        with pytest.raises(ValueError):
            error_function()

        # Check error was logged
        error_logs = [record for record in caplog.records if record.levelname == 'ERROR']
        assert len(error_logs) > 0
        assert 'error_function' in error_logs[0].message
        assert 'ValueError' in error_logs[0].message

    def test_log_file_creation(self, performance_monitor):
        """Test that log file is created."""
        assert os.path.exists(performance_monitor.log_path)
        assert os.path.getsize(performance_monitor.log_path) > 0