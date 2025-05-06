import time
import logging
from typing import Callable, Optional
from functools import wraps

class CleanupPerformanceMonitor:
    """
    A performance monitoring class for tracking cleanup job metrics.
    
    This class provides decorators and methods to monitor the performance 
    of cleanup jobs, tracking execution time, memory usage, and logging 
    important performance statistics.
    """
    
    @staticmethod
    def track_performance(log_level: int = logging.INFO) -> Callable:
        """
        A decorator to track the performance of a cleanup job method.
        
        Args:
            log_level (int): Logging level for performance metrics. 
                             Defaults to logging.INFO.
        
        Returns:
            Callable: Decorated function with performance tracking.
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                logger = logging.getLogger(__name__)
                start_time = time.time()
                
                try:
                    # Capture memory before execution (if possible)
                    import psutil
                    process = psutil.Process()
                    memory_before = process.memory_info().rss / 1024 / 1024  # MB
                except ImportError:
                    memory_before = None
                
                # Execute the function
                result = func(*args, **kwargs)
                
                # Calculate execution time
                end_time = time.time()
                execution_time = end_time - start_time
                
                # Capture memory after execution (if possible)
                try:
                    memory_after = process.memory_info().rss / 1024 / 1024  # MB
                    memory_delta = memory_after - memory_before if memory_before is not None else None
                except Exception:
                    memory_delta = None
                
                # Log performance metrics
                logger.log(
                    log_level, 
                    f"Performance Metrics for {func.__name__}: "
                    f"Execution Time = {execution_time:.4f} seconds, "
                    f"Memory Delta = {memory_delta:.2f} MB" if memory_delta is not None 
                    else f"Execution Time = {execution_time:.4f} seconds"
                )
                
                return result
            return wrapper
        return decorator
    
    @staticmethod
    def measure_cleanup_time(func: Optional[Callable] = None, *, 
                              warn_threshold: float = 10.0, 
                              error_threshold: float = 30.0) -> Callable:
        """
        A decorator to measure cleanup job time and raise warnings or errors 
        based on execution time thresholds.
        
        Args:
            func (Optional[Callable]): Function to decorate
            warn_threshold (float): Time in seconds to trigger a warning log
            error_threshold (float): Time in seconds to trigger an error log
        
        Returns:
            Callable: Decorated function with time measurement
        """
        def decorator(cleanup_func: Callable) -> Callable:
            @wraps(cleanup_func)
            def wrapper(*args, **kwargs):
                logger = logging.getLogger(__name__)
                start_time = time.time()
                
                try:
                    result = cleanup_func(*args, **kwargs)
                    
                    # Calculate execution time
                    end_time = time.time()
                    execution_time = end_time - start_time
                    
                    # Log based on thresholds
                    if execution_time > error_threshold:
                        logger.error(
                            f"Cleanup job {cleanup_func.__name__} exceeded ERROR threshold. "
                            f"Execution time: {execution_time:.2f} seconds"
                        )
                    elif execution_time > warn_threshold:
                        logger.warning(
                            f"Cleanup job {cleanup_func.__name__} exceeded WARNING threshold. "
                            f"Execution time: {execution_time:.2f} seconds"
                        )
                    
                    return result
                
                except Exception as e:
                    logger.error(f"Cleanup job {cleanup_func.__name__} failed: {str(e)}")
                    raise
            
            return wrapper
        
        # Allow decorator to be used with or without arguments
        if func is None:
            return decorator
        else:
            return decorator(func)