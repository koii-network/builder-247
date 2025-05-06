import time
import functools
import logging
from typing import Callable, Any, Dict
from prometheus_client import Summary, Counter, Histogram

class PerformanceMonitor:
    """
    A utility class for monitoring performance of cleanup jobs and other operations.
    
    Uses Prometheus client metrics to track:
    - Execution time
    - Success/failure counts
    - Detailed histogram of operation durations
    """
    
    def __init__(self, namespace: str = 'cleanup_job'):
        """
        Initialize performance metrics for a specific namespace.
        
        Args:
            namespace (str): Prefix for metric names, defaults to 'cleanup_job'
        """
        self.job_duration = Histogram(
            f'{namespace}_job_duration_seconds', 
            'Duration of cleanup job execution'
        )
        
        self.job_total_count = Counter(
            f'{namespace}_job_total_count', 
            'Total number of cleanup job runs'
        )
        
        self.job_success_count = Counter(
            f'{namespace}_job_success_count', 
            'Number of successful cleanup job runs'
        )
        
        self.job_failure_count = Counter(
            f'{namespace}_job_failure_count', 
            'Number of failed cleanup job runs'
        )
        
        self.logger = logging.getLogger(__name__)
    
    def monitor_job(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorator to monitor performance of a job function.
        
        Args:
            func (Callable): The job function to monitor
        
        Returns:
            Callable: Wrapped function with performance monitoring
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.job_total_count.inc()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                self.job_duration.observe(duration)
                self.job_success_count.inc()
                
                self.logger.info(f"Job {func.__name__} completed successfully in {duration:.2f} seconds")
                
                return result
            
            except Exception as e:
                duration = time.time() - start_time
                
                self.job_duration.observe(duration)
                self.job_failure_count.inc()
                
                self.logger.error(f"Job {func.__name__} failed after {duration:.2f} seconds: {str(e)}")
                
                raise
        
        return wrapper