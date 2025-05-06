import time
import os
import psutil
import logging
from typing import Dict, Any, Optional
from functools import wraps

class PerformanceMonitor:
    """
    A comprehensive performance monitoring utility for tracking system and function-level metrics.
    
    Supports tracking:
    - CPU usage
    - Memory usage
    - Execution time
    - Function call tracking
    """
    
    def __init__(self, log_path: Optional[str] = None):
        """
        Initialize performance monitor with optional logging configuration.
        
        :param log_path: Optional path to log performance metrics
        """
        self.log_path = log_path or os.path.join(os.getcwd(), 'performance_metrics.log')
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        
        logging.basicConfig(
            filename=self.log_path, 
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s: %(message)s'
        )
        
        # Create an empty log file to ensure its existence
        with open(self.log_path, 'a'):
            os.utime(self.log_path, None)
        
    def track_function(self, log_performance: bool = True):
        """
        Decorator to track performance of a function.
        
        :param log_performance: Whether to log performance metrics
        :return: Decorated function
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_cpu = psutil.cpu_percent()
                start_memory = psutil.virtual_memory().percent
                
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    # Log exception details
                    logging.error(f"Function {func.__name__} raised {type(e).__name__}: {str(e)}")
                    raise
                
                end_time = time.time()
                end_cpu = psutil.cpu_percent()
                end_memory = psutil.virtual_memory().percent
                
                metrics = {
                    'function_name': func.__name__,
                    'execution_time_ms': round((end_time - start_time) * 1000, 2),
                    'cpu_start_percent': start_cpu,
                    'cpu_end_percent': end_cpu,
                    'cpu_delta_percent': round(end_cpu - start_cpu, 2),
                    'memory_start_percent': start_memory,
                    'memory_end_percent': end_memory,
                    'memory_delta_percent': round(end_memory - start_memory, 2)
                }
                
                if log_performance:
                    logging.info(f"Performance Metrics: {metrics}")
                
                return result
            return wrapper
        return decorator
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Capture current system performance metrics.
        
        :return: Dictionary of system performance metrics
        """
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_used_gb': round(psutil.virtual_memory().used / (1024 * 1024 * 1024), 2),
            'memory_total_gb': round(psutil.virtual_memory().total / (1024 * 1024 * 1024), 2),
            'disk_usage_percent': psutil.disk_usage('/').percent
        }

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    Global exception handler to log unhandled exceptions with performance context.
    
    :param exc_type: Exception type
    :param exc_value: Exception value
    :param exc_traceback: Exception traceback
    """
    performance_monitor = PerformanceMonitor()
    system_metrics = performance_monitor.get_system_metrics()
    
    logging.critical(
        f"Unhandled Exception: {exc_type.__name__} - {exc_value}\n"
        f"System Metrics at Time of Crash: {system_metrics}"
    )