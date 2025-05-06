"""Utilities for signature verification."""

import base58
import nacl.signing
import json
from typing import Dict, Optional, Any, Union
from prometheus_swarm.utils.logging import log_error

# Nonce-related constants
MAX_NONCE_AGE_SECONDS = 300  # 5 minutes

class NonceError(Exception):
    """Custom exception for nonce-related errors."""
    def __init__(self, message: str, nonce_type: str = "generic"):
        """
        Initialize a NonceError with specific details.

        Args:
            message (str): Error description
            nonce_type (str, optional): Type of nonce error. Defaults to "generic".
        """
        self.nonce_type = nonce_type
        super().__init__(message)

def validate_nonce(nonce: Union[int, str], max_age: int = MAX_NONCE_AGE_SECONDS) -> bool:
    """
    Validate a nonce for replay attack prevention.

    Args:
        nonce (int or str): The nonce to validate
        max_age (int, optional): Maximum age of nonce in seconds. Defaults to 5 minutes.

    Raises:
        NonceError: If nonce is invalid

    Returns:
        bool: True if nonce is valid
    """
    try:
        import time

        # Convert nonce to integer
        nonce_value = int(nonce)

        # Current time
        current_time = int(time.time())

        # Check nonce age
        if current_time - nonce_value > max_age:
            raise NonceError(
                f"Nonce is too old (age exceeds {max_age} seconds)",
                nonce_type="age_expired"
            )

        # Log successful nonce validation
        log_error(f"Nonce {nonce} validated successfully", context="nonce_validation")
        return True

    except ValueError:
        raise NonceError("Invalid nonce format", nonce_type="format_error")
    except Exception as e:
        raise NonceError(f"Unexpected nonce validation error: {str(e)}", nonce_type="unexpected")

def verify_signature_with_nonce(
    signed_message: str,
    staking_key: str,
    expected_values: Optional[Dict[str, Any]] = None,
    nonce_check: bool = True
) -> Dict[str, Union[Dict[str, Any], str]]:
    """
    Verify a signature with optional nonce validation.

    Args:
        signed_message (str): Base58 encoded signed message
        staking_key (str): Base58 encoded public key
        expected_values (dict, optional): Dictionary of key-value pairs to validate
        nonce_check (bool, optional): Whether to perform nonce validation. Defaults to True.

    Returns:
        dict: Verification result with data or error
    """
    # First verify the signature
    result = verify_signature(signed_message, staking_key)
    if result.get("error"):
        log_error(
            Exception("Signature verification failed"),
            context=f"Signature verification failed: {result.get('error')}",
        )
        return result

    try:
        # Parse the decoded message as JSON
        data = json.loads(result["data"])

        # Validate nonce if enabled
        if nonce_check and 'nonce' in data:
            try:
                validate_nonce(data['nonce'])
            except NonceError as ne:
                log_error(
                    ne,
                    context=f"Nonce validation error: {ne.nonce_type}"
                )
                return {"error": str(ne)}

        # If we have expected values, verify them
        if expected_values:
            for key, value in expected_values.items():
                if data.get(key) != value:
                    log_error(
                        Exception("Invalid payload"),
                        context=f"Invalid payload: expected {key}={value}, got {data.get(key)}",
                    )
                    return {
                        "error": f"Invalid payload: expected {key}={value}, got {data.get(key)}"
                    }

        return {"data": data}
    except json.JSONDecodeError:
        return {"error": "Failed to parse signature payload as JSON"}
    except Exception as e:
        return {"error": f"Error validating signature payload: {str(e)}"}

# Re-export original functions for backward compatibility
__all__ = [
    'verify_signature',
    'verify_and_parse_signature',
    'verify_signature_with_nonce',
    'validate_nonce',
    'NonceError'
]