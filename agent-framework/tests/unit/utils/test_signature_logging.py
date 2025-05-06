import os
import json
import pytest
import tempfile
from datetime import datetime
from prometheus_swarm.utils.signature_logging import SignatureLogger

@pytest.fixture
def temp_log_dir():
    """Create a temporary directory for logs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

def test_signature_logger_initialization(temp_log_dir):
    """Test SignatureLogger initialization creates log directory."""
    logger = SignatureLogger(log_dir=temp_log_dir)
    assert os.path.exists(temp_log_dir)
    assert isinstance(logger, SignatureLogger)

def test_log_signature(temp_log_dir, caplog):
    """Test logging a signature."""
    caplog.set_level(logging.INFO)
    logger = SignatureLogger(log_dir=temp_log_dir)
    signature = "test_signature_123"
    metadata = {"test_key": "test_value"}
    
    logger.log_signature(signature, metadata, "test_category")
    
    # Check console log
    assert signature in caplog.text
    assert "test_key" in caplog.text
    
    # Check file log
    log_file_path = os.path.join(
        temp_log_dir, 
        f'signatures_{datetime.now().strftime("%Y%m%d")}.log'
    )
    assert os.path.exists(log_file_path)
    
    with open(log_file_path, 'r') as log_file:
        last_line = log_file.readlines()[-1].strip()
        log_entry = json.loads(last_line)
        
        assert log_entry['signature'] == signature
        assert log_entry['category'] == 'test_category'
        assert log_entry['metadata'] == metadata

def test_monitor_signatures(temp_log_dir):
    """Test signature monitoring."""
    logger = SignatureLogger(log_dir=temp_log_dir)
    
    # Log multiple signatures
    signatures_to_monitor = ['sig1', 'sig2', 'sig3']
    for sig in signatures_to_monitor:
        logger.log_signature(sig)
    
    # Monitor signatures
    results = logger.monitor_signatures(signatures_to_monitor, threshold=10)
    
    assert isinstance(results, dict)
    for sig in signatures_to_monitor:
        assert sig in results
        assert results[sig] == 1

def test_high_frequency_signature_warning(temp_log_dir, caplog):
    """Test warning for high-frequency signatures."""
    caplog.set_level(logging.WARNING)
    logger = SignatureLogger(log_dir=temp_log_dir)
    
    # Log a signature multiple times
    signature = "high_freq_sig"
    for _ in range(11):
        logger.log_signature(signature)
    
    # Monitor signatures
    results = logger.monitor_signatures([signature], threshold=10)
    
    assert results[signature] == 11
    assert "exceeded threshold" in caplog.text