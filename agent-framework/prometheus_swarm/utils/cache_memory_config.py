import psutil
import os
import logging

class CacheMemoryConfigurator:
    """
    A utility class to configure cache performance and memory limits.
    
    This class provides methods to:
    - Set process memory limits
    - Configure system-level memory management
    - Optimize cache performance
    """
    
    def __init__(self, max_memory_percent=80, min_free_memory_percent=20):
        """
        Initialize the CacheMemoryConfigurator.
        
        Args:
            max_memory_percent (int, optional): Maximum percentage of total memory 
                a process can use. Defaults to 80.
            min_free_memory_percent (int, optional): Minimum percentage of free 
                system memory to maintain. Defaults to 20.
        """
        self.max_memory_percent = max_memory_percent
        self.min_free_memory_percent = min_free_memory_percent
        self.logger = logging.getLogger(__name__)
    
    def set_process_memory_limit(self):
        """
        Set memory limit for the current process.
        
        Raises:
            RuntimeError: If setting memory limit fails.
        """
        try:
            total_memory = psutil.virtual_memory().total
            max_memory_bytes = int(total_memory * (self.max_memory_percent / 100))
            
            # Attempt to set memory limit using resource module
            try:
                import resource
                resource.setrlimit(resource.RLIMIT_AS, (max_memory_bytes, max_memory_bytes))
                self.logger.info(f"Process memory limit set to {max_memory_bytes} bytes")
            except (ImportError, ValueError, resource.error) as e:
                self.logger.warning(f"Unable to set memory limit via resource module: {e}")
                
        except Exception as e:
            self.logger.error(f"Failed to set process memory limit: {e}")
            raise RuntimeError(f"Memory limit configuration failed: {e}")
    
    def optimize_system_cache(self):
        """
        Optimize system cache performance.
        
        This method sets system-level cache parameters to improve performance.
        
        Raises:
            PermissionError: If system parameters cannot be modified.
        """
        try:
            # Tune vm.swappiness to reduce swap usage
            os.system('sysctl -w vm.swappiness=10')
            
            # Adjust cache pressure
            os.system('sysctl -w vm.vfs_cache_pressure=50')
            
            self.logger.info("System cache optimizations applied")
        except Exception as e:
            self.logger.error(f"Cache optimization failed: {e}")
            raise PermissionError(f"Unable to modify system cache parameters: {e}")
    
    def check_system_memory_health(self):
        """
        Check system memory health and log warnings if memory is low.
        
        Returns:
            bool: True if system memory is healthy, False otherwise.
        """
        memory = psutil.virtual_memory()
        available_percent = memory.available / memory.total * 100
        
        if available_percent < self.min_free_memory_percent:
            self.logger.warning(
                f"Low system memory: {available_percent:.2f}% available "
                f"(below {self.min_free_memory_percent}% threshold)"
            )
            return False
        
        return True
    
    def configure(self):
        """
        Apply all memory and cache configurations.
        
        Returns:
            bool: True if all configurations were successful, False otherwise.
        """
        try:
            self.set_process_memory_limit()
            self.optimize_system_cache()
            memory_health = self.check_system_memory_health()
            
            return memory_health
        except Exception as e:
            self.logger.error(f"Configuration failed: {e}")
            return False