import time
import pytest
from prometheus_swarm.security.replay_attack import ReplayAttackDetector

class TestReplayAttackDetector:
    def test_initial_unique_request(self):
        """Test that the first request is always considered unique"""
        detector = ReplayAttackDetector()
        request = {"user": "test", "action": "login"}
        assert detector.is_unique_request(request) is True
    
    def test_same_request_within_window(self):
        """Test that the same request within the time window is detected as a replay"""
        detector = ReplayAttackDetector(window_seconds=60)
        request = {"user": "test", "action": "login"}
        
        # First request is unique
        assert detector.is_unique_request(request) is True
        
        # Second request with same content is a replay
        assert detector.is_unique_request(request) is False
    
    def test_different_requests(self):
        """Test that different requests are treated as unique"""
        detector = ReplayAttackDetector()
        request1 = {"user": "test1", "action": "login"}
        request2 = {"user": "test2", "action": "logout"}
        
        assert detector.is_unique_request(request1) is True
        assert detector.is_unique_request(request2) is True
    
    def test_request_after_time_window(self, monkeypatch):
        """Test that a request becomes unique again after the time window"""
        class MockTime:
            _time = 0
            @classmethod
            def time(cls):
                return cls._time
        
        monkeypatch.setattr(time, 'time', MockTime.time)
        
        detector = ReplayAttackDetector(window_seconds=2)
        request = {"user": "test", "action": "login"}
        
        # First request
        MockTime._time = 0
        assert detector.is_unique_request(request) is True
        
        # Replay within window
        MockTime._time = 1
        assert detector.is_unique_request(request) is False
        
        # After window expires
        MockTime._time = 3
        assert detector.is_unique_request(request) is True
    
    def test_max_cache_size(self):
        """Test that the cache doesn't grow beyond max_cache_size"""
        detector = ReplayAttackDetector(max_cache_size=3)
        
        # Add requests to fill and exceed cache
        requests = [
            {"user": f"test{i}"} for i in range(5)
        ]
        
        unique_count = sum(detector.is_unique_request(req) for req in requests)
        
        # Verify all requests were initially unique
        assert unique_count == 5
        
        # Cache size should not exceed max_cache_size, 
        # allowing for small timing inconsistencies
        assert len(detector._request_cache) <= 3
    
    def test_request_hashability(self):
        """Test that different request representations generate the same signature"""
        detector = ReplayAttackDetector()
        
        request1 = {"a": 1, "b": 2}
        request2 = {"b": 2, "a": 1}
        
        assert detector.is_unique_request(request1) is True
        assert detector.is_unique_request(request2) is False