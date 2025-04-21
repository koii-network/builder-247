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


def parse_repo_info(repo_url: str) -> Tuple[str, str]:
    """Parse repository owner and name from a GitHub URL."""
    parts = repo_url.strip("/").split("/")
    if len(parts) >= 2:
        return parts[-2], parts[-1]
    return "", ""


def extract_section(text: str, section_name: str) -> str:
    """Extract a section from markdown-formatted text."""
    if not text:
        return ""

    lines = text.split("\n")
    section_start = None
    section_end = None

    for i, line in enumerate(lines):
        if line.strip() == f"## {section_name}":
            section_start = i + 1
        elif section_start and line.startswith("## "):
            section_end = i
            break

    if section_start is None:
        return ""

    if section_end is None:
        section_end = len(lines)

    section_text = "\n".join(lines[section_start:section_end]).strip()
    return section_text


class KeyPairManager:
    """Manages keypairs for test roles."""

    def __init__(self, keypair_paths: Dict[str, Dict[str, str]]):
        """
        Initialize with a mapping of role names to keypair paths.
        Example:
        {
            "role1": {
                "staking": "/path/to/staking/keypair",
                "public": "/path/to/public/keypair"
            }
        }
        """
        self.keypair_paths = keypair_paths
        self._keypairs = {}

    def get_keys(self, role: str) -> Dict[str, str]:
        """Get the staking and public keys for a role."""
        if role not in self.keypair_paths:
            return {"staking_key": "dummy_staking_key", "pub_key": "dummy_pub_key"}

        try:
            if role not in self._keypairs:
                paths = self.keypair_paths[role]
                staking_key = None
                pub_key = None

                if paths.get("staking"):
                    _, staking_key = load_keypair(paths["staking"])
                if paths.get("public"):
                    _, pub_key = load_keypair(paths["public"])

                self._keypairs[role] = {
                    "staking_key": staking_key or "dummy_staking_key",
                    "pub_key": pub_key or "dummy_pub_key",
                }

            return self._keypairs[role]

        except Exception as e:
            print(f"Error getting keys for {role}: {e}")
            return {"staking_key": "dummy_staking_key", "pub_key": "dummy_pub_key"}

    def create_signature(
        self, role: str, payload: Dict[str, Any], key_type: str = "staking"
    ) -> str:
        """Create a signature for a payload using a role's keypair."""
        try:
            if role not in self.keypair_paths:
                return "dummy_signature"

            keypair_path = self.keypair_paths[role].get(key_type)
            if not keypair_path:
                return "dummy_signature"

            signing_key, _ = load_keypair(keypair_path)
            return create_signature(signing_key, payload)

        except Exception as e:
            print(f"Error creating signature for {role}: {e}")
            return "dummy_signature"
