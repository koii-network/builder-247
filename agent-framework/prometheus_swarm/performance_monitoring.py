import time
import functools
import logging
from typing import Callable, Any, Dict
from contextlib import contextmanager

class PerformanceMonitor:
    """
    A class for monitoring performance metrics of function calls and code blocks.
    """

    def __init__(self, logger: logging.Logger = None):
        """
        Initialize the performance monitor.

        Args:
            logger (logging.Logger, optional): Logger for recording performance metrics. 
                                               Defaults to a basic logger if not provided.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.metrics: Dict[str, Dict[str, float]] = {}

    def record_metric(self, name: str, value: float) -> None:
        """
        Record a performance metric.

        Args:
            name (str): Name of the metric.
            value (float): Value of the metric.
        """
        if name not in self.metrics:
            self.metrics[name] = {
                'total_time': 0.0,
                'total_calls': 0,
                'min_time': float('inf'),
                'max_time': 0.0
            }

        metrics = self.metrics[name]
        metrics['total_time'] += value
        metrics['total_calls'] += 1
        metrics['min_time'] = min(metrics['min_time'], value)
        metrics['max_time'] = max(metrics['max_time'], value)

    def get_metrics(self, name: str = None) -> Dict[str, Dict[str, float]]:
        """
        Retrieve performance metrics.

        Args:
            name (str, optional): Specific metric name. If None, returns all metrics.

        Returns:
            Dict[str, Dict[str, float]]: Performance metrics.
        """
        return self.metrics.get(name, self.metrics) if name else self.metrics

    def log_metrics(self) -> None:
        """
        Log all recorded performance metrics.
        """
        for name, metric in self.metrics.items():
            if metric['total_calls'] > 0:
                avg_time = metric['total_time'] / metric['total_calls']
                self.logger.info(f"Performance Metrics for {name}:")
                self.logger.info(f"  Total Calls: {metric['total_calls']}")
                self.logger.info(f"  Total Time: {metric['total_time']:.4f}s")
                self.logger.info(f"  Average Time: {avg_time:.4f}s")
                self.logger.info(f"  Min Time: {metric['min_time']:.4f}s")
                self.logger.info(f"  Max Time: {metric['max_time']:.4f}s")

    def time_function(self, func: Callable) -> Callable:
        """
        Decorator to automatically time and record metrics for a function.

        Args:
            func (Callable): Function to be timed.

        Returns:
            Callable: Wrapped function with performance tracking.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                execution_time = end_time - start_time
                self.record_metric(func.__name__, execution_time)

        return wrapper

    @contextmanager
    def track_performance(self, name: str):
        """
        Context manager to track performance of a code block.

        Args:
            name (str): Name of the performance metric.
        """
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            self.record_metric(name, execution_time)

# Global performance monitor instance
performance_monitor = PerformanceMonitor()