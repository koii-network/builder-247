import time
import logging
import pytest
from prometheus_swarm.performance_monitoring.cleanup_job_monitor import CleanupJobPerformanceMonitor

class TestCleanupJobPerformanceMonitor:
    @pytest.fixture
    def mock_logger(self, caplog):
        """Create a capture log fixture for logging tests."""
        caplog.set_level(logging.INFO)
        return caplog
    
    def test_track_performance_decorator(self, mock_logger):
        """Test the performance tracking decorator."""
        @CleanupJobPerformanceMonitor.track_performance(label="test_cleanup")
        def sample_cleanup_job():
            time.sleep(0.1)  # Simulate some work
            return "Job completed"
        
        result = sample_cleanup_job()
        
        assert result == "Job completed"
        
        # Check log contains performance metrics
        performance_log = [record for record in mock_logger.records if "Performance Metrics" in record.message]
        assert len(performance_log) == 1
        
        log_message = performance_log[0].message
        assert "test_cleanup" in log_message
        assert "Execution Time:" in log_message
        assert "Memory Used:" in log_message
    
    def test_track_performance_exception(self, mock_logger):
        """Test performance tracking when an exception occurs."""
        @CleanupJobPerformanceMonitor.track_performance(label="failing_job")
        def failing_job():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            failing_job()
        
        # Check that the error is logged
        error_log = [record for record in mock_logger.records if "Performance tracking failed" in record.message]
        assert len(error_log) == 1
    
    def test_log_cleanup_metrics(self, mock_logger):
        """Test logging custom cleanup metrics."""
        metrics = {
            "files_processed": 100,
            "total_size_cleaned": "500MB",
            "duration": "2 minutes"
        }
        
        CleanupJobPerformanceMonitor.log_cleanup_metrics(metrics)
        
        # Check custom metrics are logged
        metric_logs = [record for record in mock_logger.records if "Cleanup Job Metrics:" in record.message]
        assert len(metric_logs) == 1  # Only one header log
        
        logged_items = [record.message for record in mock_logger.records 
                        if record.message not in ["Cleanup Job Metrics:"]]
        
        # Verify each metric is logged correctly
        for key, value in metrics.items():
            assert any(f"{key}: {value}" in item for item in logged_items)