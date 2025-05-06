import os
import psutil
import time
import threading
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class PerformanceMetrics:
    """
    Dataclass to represent system and process performance metrics.
    """
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_usage_percent: Optional[float] = None
    network_sent_mb: Optional[float] = None
    network_recv_mb: Optional[float] = None
    timestamp: float = time.time()

class PerformanceMonitor:
    """
    A comprehensive performance monitoring utility for tracking system resources.
    """
    def __init__(self, 
                 log_interval: int = 60, 
                 logger: Optional[logging.Logger] = None):
        """
        Initialize the performance monitor.

        Args:
            log_interval (int): Interval in seconds between performance log entries
            logger (Optional[logging.Logger]): Custom logger instance
        """
        self._log_interval = log_interval
        self._logger = logger or logging.getLogger(__name__)
        self._stop_event = threading.Event()
        self._monitoring_thread: Optional[threading.Thread] = None
        self._initial_network_counters: Optional[psutil._common.snetio] = None
        
    def _get_performance_metrics(self) -> PerformanceMetrics:
        """
        Collect current system performance metrics.

        Returns:
            PerformanceMetrics: Snapshot of current system performance
        """
        try:
            # CPU and Memory Metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Disk Usage
            try:
                disk_usage = psutil.disk_usage('/').percent
            except Exception:
                disk_usage = None
            
            # Network Metrics
            network_counters = psutil.net_io_counters()
            if self._initial_network_counters is None:
                self._initial_network_counters = network_counters
                network_sent = 0
                network_recv = 0
            else:
                network_sent = (network_counters.bytes_sent - self._initial_network_counters.bytes_sent) / (1024 * 1024)
                network_recv = (network_counters.bytes_recv - self._initial_network_counters.bytes_recv) / (1024 * 1024)

            return PerformanceMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                memory_total_mb=memory.total / (1024 * 1024),
                disk_usage_percent=disk_usage,
                network_sent_mb=network_sent,
                network_recv_mb=network_recv
            )
        except Exception as e:
            self._logger.error(f"Error collecting performance metrics: {e}")
            return PerformanceMetrics(
                cpu_percent=0,
                memory_percent=0,
                memory_used_mb=0,
                memory_total_mb=0
            )

    def start_monitoring(self, callback: Optional[callable] = None) -> None:
        """
        Start continuous performance monitoring in a background thread.

        Args:
            callback (Optional[callable]): Optional function to process metrics
        """
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._logger.warning("Performance monitoring is already running.")
            return

        def monitor_loop():
            while not self._stop_event.is_set():
                metrics = self._get_performance_metrics()
                
                # Log metrics
                self._logger.info(f"Performance Metrics: {metrics}")
                
                # Optional callback
                if callback:
                    try:
                        callback(asdict(metrics))
                    except Exception as e:
                        self._logger.error(f"Error in performance metrics callback: {e}")
                
                # Wait for next interval
                self._stop_event.wait(self._log_interval)

        self._stop_event.clear()
        self._monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitoring_thread.start()
        self._logger.info("Performance monitoring started.")

    def stop_monitoring(self) -> None:
        """
        Stop the performance monitoring thread.
        """
        if self._monitoring_thread:
            self._stop_event.set()
            self._monitoring_thread.join(timeout=5)
            self._logger.info("Performance monitoring stopped.")

    def get_current_metrics(self) -> Dict[str, Any]:
        """
        Get current performance metrics immediately.

        Returns:
            Dict[str, Any]: Current performance metrics
        """
        return asdict(self._get_performance_metrics())