import time
import functools
import logging
import psutil
import memory_profiler

class PerformanceMonitor:
    """
    A comprehensive performance monitoring utility for tracking 
    method execution time, memory usage, and system resource consumption.
    """
    
    @staticmethod
    def track_performance(log_level=logging.INFO):
        """
        Decorator for tracking method performance metrics.
        
        Args:
            log_level (int): Logging level for performance metrics
        
        Returns:
            Callable: Decorator function
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Track start time and memory
                start_time = time.time()
                start_memory = memory_profiler.memory_usage()[0]
                
                # CPU and system tracking
                cpu_start = psutil.cpu_percent()
                
                try:
                    # Execute the function
                    result = func(*args, **kwargs)
                    
                    # Calculate performance metrics
                    end_time = time.time()
                    end_memory = memory_profiler.memory_usage()[0]
                    cpu_end = psutil.cpu_percent()
                    
                    # Log performance metrics
                    logging.log(log_level, f"Performance Metrics for {func.__name__}:")
                    logging.log(log_level, f"Execution Time: {end_time - start_time:.4f} seconds")
                    logging.log(log_level, f"Memory Usage: {end_memory - start_memory:.2f} MiB")
                    logging.log(log_level, f"CPU Usage: {cpu_end}%")
                    
                    return result
                
                except Exception as e:
                    logging.error(f"Error in performance tracking for {func.__name__}: {e}")
                    raise
            
            return wrapper
        return decorator
    
    @staticmethod
    def get_system_metrics():
        """
        Retrieve current system resource metrics.
        
        Returns:
            dict: System metrics including CPU, memory, and disk usage
        """
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_usage": {
                "total": psutil.virtual_memory().total / (1024 * 1024),  # Total memory in MB
                "available": psutil.virtual_memory().available / (1024 * 1024),  # Available memory in MB
                "percent": psutil.virtual_memory().percent
            },
            "disk_usage": {
                "total": psutil.disk_usage('/').total / (1024 * 1024 * 1024),  # Total disk in GB
                "used": psutil.disk_usage('/').used / (1024 * 1024 * 1024),  # Used disk in GB
                "percent": psutil.disk_usage('/').percent
            }
        }