import base64
import hashlib
import json
import uuid

def generate_signature(payload, secret_key=None):
    """
    Generate a cryptographic signature for a given payload.

    Args:
        payload (dict): The payload to be signed
        secret_key (str, optional): A secret key for additional security. Defaults to None.

    Returns:
        dict: A dictionary containing signature details
        {
            'signature': base64 encoded signature,
            'id': unique identifier for the signature,
            'timestamp': generation timestamp
        }

    Raises:
        TypeError: If payload is not a dictionary
        ValueError: If payload is empty
    """
    # Validate input
    if not isinstance(payload, dict):
        raise TypeError("Payload must be a dictionary")
    
    if not payload:
        raise ValueError("Payload cannot be empty")

    # Create a deterministic JSON representation of the payload
    sorted_payload = json.dumps(payload, sort_keys=True)
    
    # Generate a unique identifier
    signature_id = str(uuid.uuid4())
    
    # Create hash components
    payload_hash = hashlib.sha256(sorted_payload.encode()).hexdigest()
    
    # Optional secret key integration
    if secret_key:
        payload_hash = hashlib.sha256((payload_hash + secret_key).encode()).hexdigest()
    
    # Base64 encode for compact representation
    signature = base64.b64encode(payload_hash.encode()).decode()
    
    return {
        'signature': signature,
        'id': signature_id,
        'timestamp': str(uuid.uuid1().time)
    }

def verify_signature(payload, signature_data, secret_key=None):
    """
    Verify the integrity of a signature.

    Args:
        payload (dict): The payload to verify
        signature_data (dict): Signature details to verify against
        secret_key (str, optional): A secret key for additional security. Defaults to None.

    Returns:
        bool: Whether the signature is valid
    """
    try:
        generated_signature = generate_signature(payload, secret_key)
        return (
            generated_signature['signature'] == signature_data.get('signature') and
            generated_signature['id'] == signature_data.get('id')
        )
    except (TypeError, ValueError):
        return False