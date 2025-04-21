import json
import base58
from nacl.signing import SigningKey
from typing import Dict, Any, Tuple


def load_keypair(keypair_path: str) -> Tuple[SigningKey, str]:
    """Load a keypair from file and return signing key and public key."""
    with open(keypair_path) as f:
        keypair_bytes = bytes(json.load(f))
        private_key = keypair_bytes[:32]
        signing_key = SigningKey(private_key)
        verify_key = signing_key.verify_key
        public_key = base58.b58encode(bytes(verify_key)).decode("utf-8")
        return signing_key, public_key


def create_signature(signing_key: SigningKey, payload: Dict[str, Any]) -> str:
    """Create a signature for a payload using the signing key."""
    # Convert payload to string with sorted keys
    payload_str = json.dumps(payload, sort_keys=True).encode()

    # Create signature
    signed = signing_key.sign(payload_str)

    # Combine signature with payload
    combined = signed.signature + payload_str

    # Encode combined data
    return base58.b58encode(combined).decode()
