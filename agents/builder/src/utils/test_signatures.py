import json
import base58
import nacl.signing
from typing import Dict, Any, Tuple


def load_keypair(keypair_path: str) -> Tuple[nacl.signing.SigningKey, str]:
    """Load a Solana keypair from a JSON file and return the signing key and public key.

    Args:
        keypair_path: Path to the JSON file containing the keypair

    Returns:
        Tuple containing:
        - SigningKey: The nacl signing key object
        - str: The base58 encoded public key
    """
    with open(keypair_path) as f:
        keypair_data = json.load(f)

    # Solana keypair files contain an array of integers representing the private key
    private_key_bytes = bytes(keypair_data)
    signing_key = nacl.signing.SigningKey(private_key_bytes)

    # Get the verify key (public key) and encode it in base58
    verify_key = signing_key.verify_key
    public_key = base58.b58encode(bytes(verify_key)).decode("utf-8")

    return signing_key, public_key


def create_test_signatures(
    payload: Dict[str, Any], staking_keypair_path: str, public_keypair_path: str
) -> Dict[str, str]:
    """Create test signatures using the provided keypairs.

    Args:
        payload: The data to sign
        staking_keypair_path: Path to the staking keypair JSON file
        public_keypair_path: Path to the public keypair JSON file

    Returns:
        Dict containing:
        - staking_key: Base58 encoded staking public key
        - pub_key: Base58 encoded public key
        - staking_signature: Base58 encoded signature using staking keypair
        - public_signature: Base58 encoded signature using public keypair
    """
    # Load keypairs
    staking_signing_key, staking_key = load_keypair(staking_keypair_path)
    public_signing_key, pub_key = load_keypair(public_keypair_path)

    # Create signatures
    payload_bytes = json.dumps(payload).encode("utf-8")
    staking_signature = base58.b58encode(
        staking_signing_key.sign(payload_bytes)
    ).decode("utf-8")
    public_signature = base58.b58encode(public_signing_key.sign(payload_bytes)).decode(
        "utf-8"
    )

    return {
        "staking_key": staking_key,
        "pub_key": pub_key,
        "staking_signature": staking_signature,
        "public_signature": public_signature,
    }
