"""
Utility module for configuring cache performance and memory limits.

This module provides functionality to manage cache performance 
and set memory constraints for the application.
"""

import os
import psutil
import logging

class CachePerformanceConfig:
    """
    A utility class for configuring cache performance and memory limits.
    """

    def __init__(self, logger=None):
        """
        Initialize the CachePerformanceConfig.

        Args:
            logger (logging.Logger, optional): Logger instance. 
                If not provided, a default logger will be created.
        """
        self.logger = logger or logging.getLogger(__name__)

    def get_system_memory(self):
        """
        Get the total system memory.

        Returns:
            int: Total system memory in bytes.
        """
        return psutil.virtual_memory().total

    def calculate_cache_limits(self, 
                                total_memory=None, 
                                max_cache_percentage=0.3, 
                                min_cache_mb=100, 
                                max_cache_mb=2048):
        """
        Calculate appropriate cache limits based on system memory.

        Args:
            total_memory (int, optional): Total system memory in bytes. 
                If not provided, will be automatically detected.
            max_cache_percentage (float, optional): Maximum percentage of 
                system memory to use for cache. Defaults to 0.3 (30%).
            min_cache_mb (int, optional): Minimum cache size in megabytes. 
                Defaults to 100 MB.
            max_cache_mb (int, optional): Maximum cache size in megabytes. 
                Defaults to 2048 MB.

        Returns:
            int: Recommended cache size in bytes.
        """
        total_memory = total_memory or self.get_system_memory()
        
        # Calculate cache size based on percentage
        cache_size_bytes = int(total_memory * max_cache_percentage)
        
        # Convert to megabytes
        cache_size_mb = cache_size_bytes // (1024 * 1024)
        
        # Ensure cache size is within min and max limits
        cache_size_mb = max(min_cache_mb, min(cache_size_mb, max_cache_mb))
        
        return cache_size_mb * 1024 * 1024  # Convert back to bytes

    def set_memory_limit(self, limit_bytes=None):
        """
        Set a memory limit for the current process.

        Args:
            limit_bytes (int, optional): Memory limit in bytes. 
                If not provided, uses calculated system-based limit.

        Returns:
            bool: True if limit was set successfully, False otherwise.
        """
        try:
            if limit_bytes is None:
                limit_bytes = self.calculate_cache_limits()
            
            # Set memory limit using resource module
            import resource
            resource.setrlimit(resource.RLIMIT_AS, (limit_bytes, limit_bytes))
            
            self.logger.info(f"Memory limit set to {limit_bytes} bytes")
            return True
        except Exception as e:
            self.logger.error(f"Could not set memory limit: {e}")
            return False

    def optimize_cache_performance(self, 
                                   cache_size_bytes=None, 
                                   eviction_policy='lru'):
        """
        Optimize cache performance with given parameters.

        Args:
            cache_size_bytes (int, optional): Cache size in bytes. 
                If not provided, will be calculated automatically.
            eviction_policy (str, optional): Cache eviction policy. 
                Defaults to 'lru' (Least Recently Used).

        Returns:
            dict: Configuration details for cache optimization.
        """
        if cache_size_bytes is None:
            cache_size_bytes = self.calculate_cache_limits()
        
        config = {
            'max_size': cache_size_bytes,
            'eviction_policy': eviction_policy
        }
        
        self.logger.info(f"Cache performance optimized: {config}")
        return config