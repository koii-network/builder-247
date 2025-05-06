import time
import psutil
import prometheus_client
from prometheus_client import Counter, Gauge, Summary, start_http_server

class AgentMetrics:
    """
    A comprehensive metrics collection class for the agent framework.
    Exposes system and application performance metrics via Prometheus.
    """
    
    def __init__(self, metrics_port=8000):
        """
        Initialize metrics with default or custom port.
        
        :param metrics_port: Port to expose Prometheus metrics endpoint
        """
        # System Resource Metrics
        self.cpu_usage = Gauge(
            'agent_cpu_usage_percent', 
            'Current CPU usage percentage'
        )
        
        self.memory_usage = Gauge(
            'agent_memory_usage_bytes', 
            'Current memory usage in bytes'
        )
        
        self.disk_usage = Gauge(
            'agent_disk_usage_percent', 
            'Current disk usage percentage'
        )
        
        # Application Performance Metrics
        self.task_counter = Counter(
            'agent_tasks_total', 
            'Total number of tasks processed'
        )
        
        self.task_duration = Summary(
            'agent_task_duration_seconds', 
            'Task processing duration in seconds'
        )
        
        self.error_counter = Counter(
            'agent_errors_total', 
            'Total number of errors encountered'
        )
        
        # Start metrics server
        start_http_server(metrics_port)
    
    def update_system_metrics(self):
        """
        Update system resource metrics.
        Collects CPU, memory, and disk usage.
        """
        self.cpu_usage.set(psutil.cpu_percent())
        self.memory_usage.set(psutil.virtual_memory().used)
        self.disk_usage.set(psutil.disk_usage('/').percent)
    
    def track_task(self):
        """
        Context manager to track task processing time and count.
        
        Usage:
            with metrics.track_task():
                # Your task processing code
        """
        return self.task_duration.time()
    
    def record_error(self, error_type):
        """
        Record an error with a specific type.
        
        :param error_type: Type or category of error
        """
        self.error_counter.labels(error_type).inc()
    
    def start_periodic_updates(self, interval=15):
        """
        Start periodic system metrics updates in background.
        
        :param interval: Update interval in seconds
        """
        def update_metrics():
            while True:
                self.update_system_metrics()
                time.sleep(interval)
        
        import threading
        update_thread = threading.Thread(target=update_metrics, daemon=True)
        update_thread.start()