import json
import hashlib
import time

def generate_replay_signature(payload: dict) -> str:
    """
    Generate a unique signature to prevent replay attacks.
    
    Args:
        payload (dict): The request payload
    
    Returns:
        str: A unique replay protection signature
    """
    # Create a deterministic, sorted representation of the payload
    sorted_payload = json.dumps(payload, sort_keys=True)
    
    # Include current timestamp to prevent exact replay
    current_time = int(time.time())
    signature_source = f"{sorted_payload}|{current_time}"
    
    # Use SHA-256 for a unique signature
    return hashlib.sha256(signature_source.encode()).hexdigest()

def add_replay_protection(payload: dict) -> dict:
    """
    Add replay protection signature to a payload.
    
    Args:
        payload (dict): The original request payload
    
    Returns:
        dict: Payload with added replay_signature
    """
    # Create a copy of the payload to avoid mutating the original
    updated_payload = payload.copy()
    
    # Add replay signature
    updated_payload['replay_signature'] = generate_replay_signature(payload)
    
    return updated_payload