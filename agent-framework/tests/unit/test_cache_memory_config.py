import pytest
import psutil
import logging
from unittest.mock import patch, MagicMock

from prometheus_swarm.utils.cache_memory_config import CacheMemoryConfigurator

class TestCacheMemoryConfigurator:
    @pytest.fixture
    def configurator(self):
        """Fixture to create a CacheMemoryConfigurator instance."""
        return CacheMemoryConfigurator(
            max_memory_percent=50, 
            min_free_memory_percent=25
        )
    
    def test_init_with_defaults(self):
        """Test initializing the configurator with default values."""
        configurator = CacheMemoryConfigurator()
        assert configurator.max_memory_percent == 80
        assert configurator.min_free_memory_percent == 20
        assert isinstance(configurator.logger, logging.Logger)
    
    @patch('psutil.virtual_memory')
    @patch('resource.setrlimit')
    def test_set_process_memory_limit_success(self, mock_setrlimit, mock_virtual_memory):
        """Test successful process memory limit setting."""
        mock_virtual_memory.return_value = MagicMock(total=10_000_000_000)  # 10 GB
        
        configurator = CacheMemoryConfigurator(max_memory_percent=50)
        configurator.set_process_memory_limit()
        
        mock_setrlimit.assert_called_once()
    
    @patch('psutil.virtual_memory')
    def test_check_system_memory_health(self, mock_virtual_memory):
        """Test system memory health check."""
        mock_memory = MagicMock(
            total=10_000_000_000,    # 10 GB total
            available=3_000_000_000  # 3 GB available
        )
        mock_virtual_memory.return_value = mock_memory
        
        configurator = CacheMemoryConfigurator(min_free_memory_percent=40)
        assert not configurator.check_system_memory_health()
        
        mock_memory.available = 5_000_000_000  # 5 GB available
        assert configurator.check_system_memory_health()
    
    @patch.object(CacheMemoryConfigurator, 'set_process_memory_limit')
    @patch.object(CacheMemoryConfigurator, 'optimize_system_cache')
    @patch.object(CacheMemoryConfigurator, 'check_system_memory_health')
    def test_configure_method(
        self, 
        mock_check_health, 
        mock_optimize_cache, 
        mock_set_memory_limit
    ):
        """Test the overall configure method."""
        mock_check_health.return_value = True
        mock_optimize_cache.return_value = None
        mock_set_memory_limit.return_value = None
        
        configurator = CacheMemoryConfigurator()
        result = configurator.configure()
        
        assert result == True
        mock_set_memory_limit.assert_called_once()
        mock_optimize_cache.assert_called_once()
        mock_check_health.assert_called_once()
    
    def test_optimize_system_cache(self, monkeypatch):
        """Test system cache optimization."""
        def mock_system(cmd):
            assert cmd in [
                'sysctl -w vm.swappiness=10', 
                'sysctl -w vm.vfs_cache_pressure=50'
            ]
            return 0
        
        monkeypatch.setattr('os.system', mock_system)
        
        configurator = CacheMemoryConfigurator()
        configurator.optimize_system_cache()