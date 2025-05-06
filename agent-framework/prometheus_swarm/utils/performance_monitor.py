import time
import logging
from functools import wraps
from typing import Callable, Any, Dict

class PerformanceMonitor:
    """
    A utility class for monitoring performance of cleanup jobs and other operations.
    
    Provides decorators and methods to track execution time, log performance metrics,
    and optionally raise warnings for long-running tasks.
    """
    
    @staticmethod
    def track_performance(
        warning_threshold: float = 60.0,  # Default 1 minute warning threshold
        log_level: int = logging.WARNING
    ) -> Callable:
        """
        Decorator to track performance of functions/methods.
        
        Args:
            warning_threshold (float): Time in seconds after which a warning is logged
            log_level (int): Logging level for performance warning
        
        Returns:
            Callable: Decorated function with performance tracking
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                
                execution_time = end_time - start_time
                
                if execution_time > warning_threshold:
                    logging.log(
                        log_level, 
                        f"Performance Warning: {func.__name__} took {execution_time:.2f} seconds"
                    )
                
                return result
            return wrapper
        return decorator

    @staticmethod
    def log_performance(
        operation_name: str, 
        start_time: float, 
        logger: logging.Logger = None
    ) -> Dict[str, float]:
        """
        Log performance metrics for an operation.
        
        Args:
            operation_name (str): Name of the operation being monitored
            start_time (float): Start time of the operation
            logger (logging.Logger, optional): Custom logger. If None, uses root logger
        
        Returns:
            Dict[str, float]: Performance metrics including execution time
        """
        end_time = time.time()
        execution_time = end_time - start_time
        
        metrics = {
            'operation': operation_name,
            'start_time': start_time,
            'end_time': end_time,
            'execution_time': execution_time
        }
        
        if logger is None:
            logger = logging.getLogger()
        
        logger.info(
            f"Performance Metrics: {operation_name} "
            f"completed in {execution_time:.2f} seconds"
        )
        
        return metrics