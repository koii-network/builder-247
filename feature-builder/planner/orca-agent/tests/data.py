import os
import json
import base58
from nacl.signing import SigningKey
from typing import Dict, Any


class DataManager:
    def __init__(self, task_id=None, round_number=None):
        # Task info
        self.task_id = task_id
        self.round_number = round_number

        # Repository info
        self.repo_owner = None
        self.repo_name = None

        # All rounds data
        self.rounds = {}

        # Current round data
        self.issue_uuid = None
        self.ipfs_cid = None
        self.submission_data = {}
        self.last_completed_step = None

        # Store keypair paths for each role
        self.keypairs = {
            "leader": {
                "staking": os.getenv("LEADER_STAKING_KEYPAIR"),
                "public": os.getenv("LEADER_PUBLIC_KEYPAIR"),
            },
            "worker1": {
                "staking": os.getenv("WORKER1_STAKING_KEYPAIR"),
                "public": os.getenv("WORKER1_PUBLIC_KEYPAIR"),
            },
            "worker2": {
                "staking": os.getenv("WORKER2_STAKING_KEYPAIR"),
                "public": os.getenv("WORKER2_PUBLIC_KEYPAIR"),
            },
        }

    def get_round_data(self):
        """Get the current round's data as a dictionary"""
        data = {
            "last_completed_step": self.last_completed_step,
            "issue_uuid": self.issue_uuid,
        }
        if self.ipfs_cid:
            data["ipfs_cid"] = self.ipfs_cid
        if self.submission_data:
            data["submission_data"] = self.submission_data
        return data

    def set_round_data(self, round_data):
        """Set the current round's data from a dictionary"""
        self.last_completed_step = round_data.get("last_completed_step")
        self.issue_uuid = round_data.get("issue_uuid")
        self.ipfs_cid = round_data.get("ipfs_cid")
        self.submission_data = round_data.get("submission_data", {})
        # Store in rounds data too
        self.rounds[str(self.round_number)] = round_data

    def clear_round_data(self):
        """Clear round-specific data when starting a new round"""
        self.ipfs_cid = None
        self.submission_data = {}
        self.last_completed_step = None

    def _load_keypair(self, keypair_path: str) -> tuple[SigningKey, str]:
        """Load a keypair from file and return signing key and public key."""
        with open(keypair_path) as f:
            keypair_bytes = bytes(json.load(f))
            private_key = keypair_bytes[:32]
            signing_key = SigningKey(private_key)
            verify_key = signing_key.verify_key
            public_key = base58.b58encode(bytes(verify_key)).decode("utf-8")
            return signing_key, public_key

    def create_signature(self, role: str, payload: Dict[str, Any]) -> Dict[str, str]:
        """Create signatures for a payload using the specified role's keypair."""
        try:
            keypair = self.keypairs[role]
            staking_keypair_path = keypair["staking"]
            public_keypair_path = keypair["public"]

            if not staking_keypair_path or not public_keypair_path:
                return {
                    "staking_key": "dummy_staking_key",
                    "pub_key": "dummy_pub_key",
                    "staking_signature": "dummy_staking_signature",
                    "public_signature": "dummy_public_signature",
                }

            # Load keypairs
            staking_signing_key, staking_key = self._load_keypair(staking_keypair_path)
            public_signing_key, pub_key = self._load_keypair(public_keypair_path)

            # Add required fields if not present
            if "pubKey" not in payload:
                payload["pubKey"] = pub_key
            if "stakingKey" not in payload:
                payload["stakingKey"] = staking_key
            if "githubUsername" not in payload:
                payload["githubUsername"] = os.getenv(f"{role.upper()}_GITHUB_USERNAME")

            # Convert payload to string with sorted keys
            payload_str = json.dumps(payload, sort_keys=True).encode()

            # Create signatures
            staking_signed = staking_signing_key.sign(payload_str)
            public_signed = public_signing_key.sign(payload_str)

            # Combine signatures with payload
            staking_combined = staking_signed.signature + payload_str
            public_combined = public_signed.signature + payload_str

            # Encode combined data
            staking_signature = base58.b58encode(staking_combined).decode()
            public_signature = base58.b58encode(public_combined).decode()

            return {
                "staking_key": staking_key,
                "pub_key": pub_key,
                "staking_signature": staking_signature,
                "public_signature": public_signature,
            }
        except Exception as e:
            print(f"Error creating signatures: {e}")
            return {
                "staking_key": "dummy_staking_key",
                "pub_key": "dummy_pub_key",
                "staking_signature": "dummy_staking_signature",
                "public_signature": "dummy_public_signature",
            }

    def prepare_worker_task(self, role: str, round_number: int) -> Dict[str, Any]:
        """Prepare payload for worker-task endpoint."""
        # Get keys first so we can use them in the payload
        keys = self.get_keys(role)

        # Create fetch-planner-todo payload for signature
        fetch_todo_payload = {
            "taskId": self.task_id,
            "roundNumber": round_number,
            "action": "fetch",
            "githubUsername": keys["staking_key"],  # Use staking key as githubUsername
            "stakingKey": keys["staking_key"],  # Include actual staking key
        }

        # Get signatures for fetch-todo
        fetch_signatures = self.create_signature(role, fetch_todo_payload)

        # The actual payload just needs signature and stakingKey
        return {
            "signature": fetch_signatures["staking_signature"],
            "stakingKey": fetch_signatures["staking_key"],
        }

    def prepare_worker_audit(
        self,
        auditor: str,
        ipfs_cid: str,
        round_number: int,
        submission_data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Prepare payload for worker-audit endpoint."""
        # Create audit payload
        audit_payload = {
            "taskId": self.task_id,
            "roundNumber": round_number,
            "action": "audit",
            "githubUsername": os.getenv(f"{auditor.upper()}_GITHUB_USERNAME"),
            "prUrl": ipfs_cid,
        }

        # Get signatures for audit
        audit_signatures = self.create_signature(auditor, audit_payload)

        return {
            "taskId": self.task_id,
            "roundNumber": round_number,
            "stakingKey": audit_signatures["staking_key"],
            "stakingSignature": audit_signatures["staking_signature"],
            "prUrl": ipfs_cid,
            "submissionData": submission_data or {},
        }

    def get_keys(self, role: str) -> Dict[str, str]:
        """Get public and staking keys for a role."""
        try:
            keypair = self.keypairs[role]
            staking_keypair_path = keypair["staking"]
            public_keypair_path = keypair["public"]

            if not staking_keypair_path or not public_keypair_path:
                return {
                    "staking_key": "dummy_staking_key",
                    "pub_key": "dummy_pub_key",
                }

            _, staking_key = self._load_keypair(staking_keypair_path)
            _, pub_key = self._load_keypair(public_keypair_path)

            return {
                "staking_key": staking_key,
                "pub_key": pub_key,
            }
        except Exception as e:
            print(f"Error getting keys: {e}")
            return {
                "staking_key": "dummy_staking_key",
                "pub_key": "dummy_pub_key",
            }
