import os
import tempfile
import pytest
from prometheus_swarm.utils.nonce_config import NonceConfigManager

def test_nonce_generation_and_validation():
    """
    Test nonce generation and validation functionality.
    """
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(delete=False) as temp_config:
        temp_config_path = temp_config.name
    
    try:
        # Initialize NonceConfigManager with temporary config
        nonce_manager = NonceConfigManager(config_path=temp_config_path)
        
        # Test nonce generation
        identifier = "test_user"
        nonce = nonce_manager.generate_nonce(identifier)
        
        # Validate the generated nonce
        assert nonce_manager.validate_nonce(identifier, nonce) is True
        
        # Validate with incorrect nonce
        assert nonce_manager.validate_nonce(identifier, "wrong_nonce") is False
    finally:
        # Clean up the temporary config file
        if os.path.exists(temp_config_path):
            os.unlink(temp_config_path)

def test_nonce_validation_edge_cases():
    """
    Test nonce validation edge cases.
    """
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(delete=False) as temp_config:
        temp_config_path = temp_config.name
    
    try:
        nonce_manager = NonceConfigManager(config_path=temp_config_path)
        
        # Test empty inputs
        assert nonce_manager.validate_nonce("", "") is False
        assert nonce_manager.validate_nonce("user", "") is False
        assert nonce_manager.validate_nonce("", "nonce") is False
        
        # Test validation of non-existent identifier
        assert nonce_manager.validate_nonce("non_existent_user", "some_nonce") is False
    finally:
        # Clean up the temporary config file
        if os.path.exists(temp_config_path):
            os.unlink(temp_config_path)

def test_nonce_generation_requirements():
    """
    Test nonce generation requirements and constraints.
    """
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(delete=False) as temp_config:
        temp_config_path = temp_config.name
    
    try:
        nonce_manager = NonceConfigManager(config_path=temp_config_path)
        
        # Test invalid nonce generation
        with pytest.raises(ValueError, match="Identifier cannot be empty"):
            nonce_manager.generate_nonce("")
        
        # Test nonce generation with different lengths
        nonce_short = nonce_manager.generate_nonce("user_short", length=16)
        nonce_long = nonce_manager.generate_nonce("user_long", length=64)
        
        assert len(nonce_short) == 32  # Hex representation of 16 bytes
        assert len(nonce_long) == 128  # Hex representation of 64 bytes
    finally:
        # Clean up the temporary config file
        if os.path.exists(temp_config_path):
            os.unlink(temp_config_path)

def test_nonce_clear_functionality():
    """
    Test nonce clearing functionality.
    """
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(delete=False) as temp_config:
        temp_config_path = temp_config.name
    
    try:
        nonce_manager = NonceConfigManager(config_path=temp_config_path)
        
        # Generate a nonce
        identifier = "test_clear_user"
        nonce = nonce_manager.generate_nonce(identifier)
        
        # Validate nonce before clearing
        assert nonce_manager.validate_nonce(identifier, nonce) is True
        
        # Clear the nonce
        nonce_manager.clear_nonce(identifier)
        
        # Validate that the nonce is no longer valid
        assert nonce_manager.validate_nonce(identifier, nonce) is False
    finally:
        # Clean up the temporary config file
        if os.path.exists(temp_config_path):
            os.unlink(temp_config_path)