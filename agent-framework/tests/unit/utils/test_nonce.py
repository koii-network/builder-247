import time
import pytest
from prometheus_swarm.utils.nonce import NonceTracker


def test_generate_nonce():
    """Test generating a unique nonce."""
    tracker = NonceTracker()
    nonce1 = tracker.generate_nonce()
    nonce2 = tracker.generate_nonce()

    assert nonce1 != nonce2, "Generated nonces should be unique"
    assert isinstance(nonce1, str), "Nonce should be a string"


def test_validate_nonce_basic():
    """Test basic nonce validation."""
    tracker = NonceTracker()
    nonce = tracker.generate_nonce()

    # First validation should succeed
    assert tracker.validate_nonce(nonce), "First nonce validation should pass"

    # Second validation should fail (nonce already used)
    assert not tracker.validate_nonce(nonce), "Second nonce validation should fail"


def test_nonce_expiration():
    """Test nonce expiration."""
    tracker = NonceTracker(max_age_seconds=1)
    nonce = tracker.generate_nonce()

    # Wait until nonce expires
    time.sleep(2)

    # Nonce should now be invalid
    assert not tracker.validate_nonce(nonce), "Expired nonce should be invalid"


def test_nonce_with_prefix():
    """Test generating nonce with a prefix."""
    tracker = NonceTracker()
    nonce = tracker.generate_nonce(prefix="test_")

    assert nonce.startswith("test_"), "Nonce should start with the provided prefix"
    assert tracker.validate_nonce(nonce), "Prefixed nonce should be valid"


def test_concurrent_nonce_handling():
    """Test concurrent nonce generation and validation."""
    tracker = NonceTracker()
    nonces = set()

    def generate_and_validate():
        nonce = tracker.generate_nonce()
        nonces.add(nonce)
        assert tracker.validate_nonce(nonce), "Concurrent nonce should be valid"

    # Simulate concurrent nonce generation
    threads = []
    for _ in range(100):
        thread = threading.Thread(target=generate_and_validate)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    # All nonces should be unique
    assert len(nonces) == 100, "All generated nonces should be unique"