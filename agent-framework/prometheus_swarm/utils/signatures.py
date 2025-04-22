"""Utilities for signature verification."""

import base58
import nacl.signing
import json
from typing import Dict, Optional, Any, Union
from prometheus_swarm.utils.logging import log_error


def verify_signature(signed_message: str, staking_key: str) -> Dict[str, Any]:
    """Verify a signature locally using PyNaCl.

    This function verifies signatures created by the Koii task node using nacl.sign().
    The signatures are base58 encoded before being sent.

    Args:
        signed_message (str): Base58 encoded signed message
        staking_key (str): Base58 encoded public key

    Returns:
        dict: Contains either:
            - data (str): The decoded message if verification succeeds
            - error (str): Error message if verification fails
    """
    try:
        # Decode base58 signature and public key
        signed_bytes = base58.b58decode(signed_message)
        pubkey_bytes = base58.b58decode(staking_key)

        # Create verify key from public key
        verify_key = nacl.signing.VerifyKey(pubkey_bytes)

        # Verify and get message
        message = verify_key.verify(signed_bytes)

        # Decode message from bytes to string
        decoded_message = message.decode("utf-8")
        return {"data": decoded_message}
    except Exception as e:
        return {"error": f"Verification failed: {str(e)}"}


def verify_and_parse_signature(
    signed_message: str,
    staking_key: str,
    expected_values: Optional[Dict[str, Any]] = None,
) -> Dict[str, Union[Dict[str, Any], str]]:
    """Verify a signature and optionally validate its contents.

    This function combines signature verification with payload validation.
    It verifies the signature, decodes the message, parses it as JSON,
    and optionally validates expected values in the payload.

    Args:
        signed_message (str): Base58 encoded signed message
        staking_key (str): Base58 encoded public key
        expected_values (dict, optional): Dictionary of key-value pairs that must be present
            and match in the decoded payload

    Returns:
        dict: Contains either:
            - data (dict): The decoded and parsed JSON payload if verification succeeds
            - error (str): Error message if verification or validation fails
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
