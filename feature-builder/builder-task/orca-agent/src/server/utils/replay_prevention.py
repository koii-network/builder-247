import hashlib
import json
import time
from typing import Dict, Any
from functools import wraps
from flask import request, jsonify

# Time window for replay prevention in seconds
REPLAY_WINDOW = 300  # 5 minutes

# In-memory store to track processed requests (can be replaced with Redis in production)
_processed_requests: Dict[str, float] = {}

def generate_request_signature(data: Dict[str, Any]) -> str:
    """
    Generate a unique signature for a request based on its payload and timestamp.
    
    Args:
        data (dict): Request payload data
    
    Returns:
        str: A unique signature for the request
    """
    # Create a deterministic, sorted representation of the request data
    sorted_data = json.dumps(data, sort_keys=True)
    
    # Include current timestamp to prevent exact replay within a time window
    current_time = int(time.time())
    signature_source = f"{sorted_data}|{current_time}"
    
    # Use SHA-256 for a unique signature
    return hashlib.sha256(signature_source.encode()).hexdigest()

def prevent_replay(func):
    """
    Decorator to prevent replay attacks on route handlers.
    
    This decorator does the following:
    1. Checks if the request payload contains a unique signature
    2. Validates the signature hasn't been processed recently
    3. Tracks processed requests to prevent replay
    
    Raises:
        Unauthorized response if the request is a potential replay
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Only apply to POST requests
        if request.method != 'POST':
            return func(*args, **kwargs)
        
        # Get request data
        try:
            request_data = request.get_json() or {}
        except Exception:
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        # Check for replay signature
        replay_signature = request_data.get('replay_signature')
        if not replay_signature:
            return jsonify({"error": "Missing replay protection signature"}), 400
        
        # Check if this signature has been processed recently
        current_time = time.time()
        if (replay_signature in _processed_requests and 
            current_time - _processed_requests[replay_signature] < REPLAY_WINDOW):
            return jsonify({"error": "Potential replay attack detected"}), 403
        
        # Remove old entries to prevent memory growth
        for sig, timestamp in list(_processed_requests.items()):
            if current_time - timestamp > REPLAY_WINDOW:
                del _processed_requests[sig]
        
        # Mark this signature as processed
        _processed_requests[replay_signature] = current_time
        
        # Continue with the route handler
        return func(*args, **kwargs)
    
    return wrapper