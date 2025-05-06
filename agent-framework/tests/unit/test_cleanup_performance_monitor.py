import pytest
import time
import logging
from unittest.mock import patch

from prometheus_swarm.monitoring.cleanup_monitor import CleanupPerformanceMonitor

def test_track_performance_decorator():
    # Create a mock logger to capture log messages
    with patch('logging.Logger.log') as mock_log:
        @CleanupPerformanceMonitor.track_performance()
        def dummy_cleanup_job():
            time.sleep(0.1)  # Simulate some work
            return "Cleaned up"
        
        result = dummy_cleanup_job()
        
        # Verify result
        assert result == "Cleaned up"
        
        # Verify logging occurred
        mock_log.assert_called_once()
        log_args = mock_log.call_args[0]
        
        # Check log level is INFO and message contains execution time
        assert log_args[0] == logging.INFO
        assert "Execution Time" in log_args[1]

def test_measure_cleanup_time_warn_threshold():
    with patch('logging.Logger.warning') as mock_warning:
        @CleanupPerformanceMonitor.measure_cleanup_time(warn_threshold=0.05)
        def slow_cleanup_job():
            time.sleep(0.1)  # Exceed warning threshold
            return "Partially cleaned"
        
        result = slow_cleanup_job()
        
        # Verify result
        assert result == "Partially cleaned"
        
        # Verify warning was logged
        mock_warning.assert_called_once()
        warning_message = mock_warning.call_args[0][0]
        assert "exceeded WARNING threshold" in warning_message

def test_measure_cleanup_time_error_threshold():
    with patch('logging.Logger.error') as mock_error:
        @CleanupPerformanceMonitor.measure_cleanup_time(error_threshold=0.05)
        def very_slow_cleanup_job():
            time.sleep(0.1)  # Exceed error threshold
            return "Slow cleanup"
        
        result = very_slow_cleanup_job()
        
        # Verify result
        assert result == "Slow cleanup"
        
        # Verify error was logged
        mock_error.assert_called_once()
        error_message = mock_error.call_args[0][0]
        assert "exceeded ERROR threshold" in error_message

def test_cleanup_job_failure():
    with patch('logging.Logger.error') as mock_error:
        @CleanupPerformanceMonitor.measure_cleanup_time()
        def failing_cleanup_job():
            raise RuntimeError("Cleanup failed")
        
        # Verify that the original exception is re-raised
        with pytest.raises(RuntimeError, match="Cleanup failed"):
            failing_cleanup_job()
        
        # Verify error was logged
        mock_error.assert_called_once()
        error_message = mock_error.call_args[0][0]
        assert "Cleanup job failing_cleanup_job failed" in error_message