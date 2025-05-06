import time
import logging
from typing import Any, Callable, Dict
from functools import wraps

class CleanupJobPerformanceMonitor:
    """
    A performance monitoring utility for tracking cleanup job metrics.
    
    This class provides decorators and methods to monitor the performance 
    of cleanup jobs, tracking key metrics like execution time, memory usage, 
    and other relevant performance indicators.
    """
    
    @staticmethod
    def track_performance(label: str = "cleanup_job"):
        """
        A decorator to track the performance of a cleanup job method.
        
        Args:
            label (str, optional): A descriptive label for the job. Defaults to "cleanup_job".
        
        Returns:
            Callable: A decorator function that wraps the original method.
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.time()
                start_memory = CleanupJobPerformanceMonitor._get_memory_usage()
                
                try:
                    result = func(*args, **kwargs)
                    end_time = time.time()
                    end_memory = CleanupJobPerformanceMonitor._get_memory_usage()
                    
                    # Log performance metrics
                    execution_time = end_time - start_time
                    memory_used = end_memory - start_memory
                    
                    logging.info(
                        f"Performance Metrics for {label}: "
                        f"Execution Time: {execution_time:.4f} seconds, "
                        f"Memory Used: {memory_used:.2f} MB"
                    )
                    
                    return result
                
                except Exception as e:
                    logging.error(f"Performance tracking failed for {label}: {str(e)}")
                    raise
            
            return wrapper
        return decorator
    
    @staticmethod
    def _get_memory_usage() -> float:
        """
        Get the current memory usage of the process.
        
        Returns:
            float: Memory usage in megabytes.
        """
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)  # Convert to MB
        except ImportError:
            logging.warning("psutil not available. Memory tracking disabled.")
            return 0.0
    
    @classmethod
    def log_cleanup_metrics(cls, metrics: Dict[str, Any]) -> None:
        """
        Log custom cleanup job metrics.
        
        Args:
            metrics (Dict[str, Any]): A dictionary of performance metrics.
        """
        logging.info("Cleanup Job Metrics:")
        for key, value in metrics.items():
            logging.info(f"{key}: {value}")