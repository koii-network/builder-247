import os
import json
import base58
from nacl.signing import SigningKey
from typing import Dict, Any
from github import Github
from prometheus_swarm.tools.github_operations.parser import extract_section


class DataManager:
    def __init__(self, task_id=None, round_number=None):
        # Task info
        self.task_id = task_id
        self.round_number = round_number

        # Repository info
        self.fork_url = None
        self.repo_owner = None
        self.repo_name = None
        self.branch_name = None

        # All rounds data
        self.rounds = {}

        # Current round data
        self.issue_uuid = None
        self.pr_urls = {}
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

    def _parse_repo_info(self):
        """Parse repository owner and name from fork URL"""
        if not self.fork_url:
            return None, None
        parts = self.fork_url.strip("/").split("/")
        if len(parts) >= 2:
            return parts[-2], parts[-1]
        return None, None

    def set_fork_url(self, url):
        """Set fork URL and update repo info"""
        self.fork_url = url
        self.repo_owner, self.repo_name = self._parse_repo_info()

    def get_round_data(self):
        """Get the current round's data as a dictionary"""
        data = {
            "last_completed_step": self.last_completed_step,
            "issue_uuid": self.issue_uuid,
        }
        if self.pr_urls:
            data["pr_urls"] = self.pr_urls
        if self.submission_data:
            data["submission_data"] = self.submission_data
        return data

    def set_round_data(self, round_data):
        """Set the current round's data from a dictionary"""
        self.last_completed_step = round_data.get("last_completed_step")
        self.issue_uuid = round_data.get("issue_uuid")
        self.pr_urls = round_data.get("pr_urls", {})
        self.submission_data = round_data.get("submission_data", {})
        # Store in rounds data too
        self.rounds[str(self.round_number)] = round_data

    def clear_round_data(self):
        """Clear round-specific data when starting a new round"""
        self.pr_urls = {}
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

    def prepare_create_aggregator_repo(
        self,
    ) -> Dict[str, Any]:
        """Prepare payload for create-aggregator-repo endpoint."""

        return {
            "taskId": self.task_id,
        }

    def prepare_worker_task(self, role: str, round_number: int) -> Dict[str, Any]:
        """Prepare payload for worker-task endpoint."""
        if not self.fork_url or not self.branch_name:
            raise Exception(
                "Fork URL and branch name must be set before preparing worker task"
            )

        # Create fetch-todo payload for stakingSignature and publicSignature
        fetch_todo_payload = {
            "taskId": self.task_id,
            "roundNumber": round_number,
            "action": "fetch-todo",
            "githubUsername": os.getenv(f"{role.upper()}_GITHUB_USERNAME"),
        }

        # Create add-pr payload for addPRSignature
        add_pr_payload = {
            "taskId": self.task_id,
            "roundNumber": round_number,
            "action": "add-todo-pr",
            "githubUsername": os.getenv(f"{role.upper()}_GITHUB_USERNAME"),
        }

        # Get signatures for fetch-todo
        fetch_signatures = self.create_signature(role, fetch_todo_payload)

        # Create addPRSignature for add-pr
        # We need to manually create this signature since our create_signature method
        # doesn't support multiple payloads in one call
        try:
            keypair = self.keypairs[role]
            staking_keypair_path = keypair["staking"]

            if not staking_keypair_path:
                add_pr_signature = "dummy_add_pr_signature"
            else:
                # Load staking keypair for add-todo-pr signature
                staking_signing_key, _ = self._load_keypair(staking_keypair_path)

                # Update add_pr_payload with staking key and pub key
                add_pr_payload["stakingKey"] = fetch_signatures["staking_key"]
                add_pr_payload["pubKey"] = fetch_signatures["pub_key"]

                # Create add-todo-pr signature
                payload_str = json.dumps(add_pr_payload, sort_keys=True).encode()
                staking_signed = staking_signing_key.sign(payload_str)
                staking_combined = staking_signed.signature + payload_str
                add_pr_signature = base58.b58encode(staking_combined).decode()
        except Exception as e:
            print(f"Error creating add-PR signature: {e}")
            add_pr_signature = "dummy_add_pr_signature"

        # Match exactly what 1-task.ts sends
        return {
            "taskId": self.task_id,
            "roundNumber": round_number,
            "stakingKey": fetch_signatures["staking_key"],
            "pubKey": fetch_signatures["pub_key"],
            "stakingSignature": fetch_signatures["staking_signature"],
            "publicSignature": fetch_signatures["public_signature"],
            "addPRSignature": add_pr_signature,
        }

    def create_submitter_signature(
        self, submitter_role: str, payload: Dict[str, Any]
    ) -> str:
        """Create signature using the submitter's staking key."""
        try:
            staking_keypair_path = self.keypairs[submitter_role]["staking"]
            if staking_keypair_path:
                staking_signing_key, _ = self._load_keypair(staking_keypair_path)
                payload_str = json.dumps(payload, sort_keys=True).encode()
                staking_signed = staking_signing_key.sign(payload_str)
                staking_combined = staking_signed.signature + payload_str
                return base58.b58encode(staking_combined).decode()
            else:
                print(f"Warning: No staking keypair path for {submitter_role}")
                return "dummy_submitter_signature"
        except Exception as e:
            print(f"Error creating submitter signature: {e}")
            return "dummy_submitter_signature"

    def prepare_worker_audit(
        self,
        auditor: str,
        pr_url: str,
        round_number: int,
        submission_data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Prepare payload for worker-audit endpoint."""
        if not submission_data:
            raise ValueError("Submission data is required for worker audit")

        # Create auditor payload which is used to generate the signature
        auditor_payload = {
            "taskId": self.task_id,
            "roundNumber": round_number,
            "prUrl": pr_url,
        }

        # Create auditor's signatures with the complete payload
        auditor_signatures = self.create_signature(auditor, auditor_payload)

        # Structure the payload according to what the server expects
        return {
            "submission": {
                "taskId": self.task_id,
                "roundNumber": round_number,
                "prUrl": pr_url,
                "githubUsername": submission_data.get("githubUsername"),
                "repoOwner": self.repo_owner,
                "repoName": self.repo_name,
                "stakingKey": submission_data.get("stakingKey"),
                "pubKey": submission_data.get("pubKey"),
                "uuid": submission_data.get("uuid"),
                "nodeType": submission_data.get("nodeType"),
            },
            "submitterSignature": submission_data.get("signature"),
            "submitterStakingKey": submission_data.get("stakingKey"),
            "submitterPubKey": submission_data.get("pubKey"),
            "prUrl": pr_url,
            "repoOwner": self.repo_owner,
            "repoName": self.repo_name,
            "githubUsername": os.getenv(f"{auditor.upper()}_GITHUB_USERNAME"),
            "stakingKey": auditor_signatures["staking_key"],
            "pubKey": auditor_signatures["pub_key"],
            "stakingSignature": auditor_signatures["staking_signature"],
            "publicSignature": auditor_signatures["public_signature"],
        }

    def prepare_leader_task(self, role: str, round_number: int) -> Dict[str, Any]:
        """Prepare payload for leader-task endpoint."""
        # Create fetch-issue payload for stakingSignature and publicSignature
        fetch_issue_payload = {
            "taskId": self.task_id,
            "roundNumber": round_number,
            "action": "fetch-issue",
            "githubUsername": os.getenv(f"{role.upper()}_GITHUB_USERNAME"),
        }

        # Create add-pr payload for addPRSignature
        add_pr_payload = {
            "taskId": self.task_id,
            "roundNumber": round_number,
            "action": "add-issue-pr",
            "githubUsername": os.getenv(f"{role.upper()}_GITHUB_USERNAME"),
        }

        # Get signatures for fetch-issue
        fetch_signatures = self.create_signature(role, fetch_issue_payload)

        # Create addPRSignature for add-pr
        try:
            keypair = self.keypairs[role]
            staking_keypair_path = keypair["staking"]

            if not staking_keypair_path:
                add_pr_signature = "dummy_add_pr_signature"
            else:
                # Load staking keypair for add-todo-pr signature
                staking_signing_key, _ = self._load_keypair(staking_keypair_path)

                # Update add_pr_payload with staking key and pub key
                add_pr_payload["stakingKey"] = fetch_signatures["staking_key"]
                add_pr_payload["pubKey"] = fetch_signatures["pub_key"]

                # Create add-todo-pr signature
                payload_str = json.dumps(add_pr_payload, sort_keys=True).encode()
                staking_signed = staking_signing_key.sign(payload_str)
                staking_combined = staking_signed.signature + payload_str
                add_pr_signature = base58.b58encode(staking_combined).decode()
        except Exception as e:
            print(f"Error creating add-PR signature: {e}")
            add_pr_signature = "dummy_add_pr_signature"

        # Match exactly what 1-task.ts sends
        return {
            "taskId": self.task_id,
            "roundNumber": round_number,
            "stakingKey": fetch_signatures["staking_key"],
            "pubKey": fetch_signatures["pub_key"],
            "stakingSignature": fetch_signatures["staking_signature"],
            "publicSignature": fetch_signatures["public_signature"],
            "addPRSignature": add_pr_signature,
        }

    def extract_staking_key_from_pr(self, pr_url: str) -> str:
        """Extract staking key from PR description"""
        parts = pr_url.strip("/").split("/")
        pr_number = int(parts[-1])
        pr_repo_owner = parts[-4]
        pr_repo_name = parts[-3]

        gh = Github(os.getenv("GITHUB_TOKEN"))
        repo = gh.get_repo(f"{pr_repo_owner}/{pr_repo_name}")
        pr = repo.get_pull(pr_number)

        staking_section = extract_section(pr.body, "STAKING_KEY")
        if not staking_section:
            raise ValueError(f"No staking key found in PR {pr_url}")

        return staking_section.split(":")[0].strip()

    def prepare_aggregator_info(self, role: str, round_number: int) -> Dict[str, Any]:
        """Prepare payload for add-aggregator-info endpoint."""
        if not self.fork_url or not self.branch_name:
            raise Exception(
                "Fork URL and branch name must be set before preparing aggregator info"
            )

        # Create the payload with all required fields
        payload = {
            "taskId": self.task_id,
            "roundNumber": round_number,
            "action": "create-repo",
            "githubUsername": os.getenv(f"{role.upper()}_GITHUB_USERNAME"),
            "issueUuid": self.branch_name,
            "aggregatorUrl": self.fork_url,
        }

        # Create signature with the complete payload
        signatures = self.create_signature(role, payload)

        # Return the final payload with signature
        return {
            "taskId": self.task_id,
            "roundNumber": round_number,
            "action": "create-repo",
            "githubUsername": os.getenv(f"{role.upper()}_GITHUB_USERNAME"),
            "stakingKey": signatures["staking_key"],
            "pubKey": signatures["pub_key"],
            "issueUuid": self.branch_name,
            "aggregatorUrl": self.fork_url,
            "signature": signatures["staking_signature"],
        }

    def prepare_leader_audit(
        self,
        auditor: str,
        pr_url: str,
        round_number: int,
        submission_data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Prepare payload for leader-audit endpoint."""
        if not submission_data:
            raise ValueError("Submission data is required for leader audit")

        # Create auditor payload (what the worker would sign to audit)
        auditor_payload = {
            "taskId": self.task_id,
            "roundNumber": round_number,
            "prUrl": pr_url,
        }

        # Create auditor's signatures
        auditor_signatures = self.create_signature(auditor, auditor_payload)

        # Structure the payload according to the audit.ts implementation
        # Use all fields from the submission_data
        return {
            "submission": {
                "taskId": self.task_id,
                "roundNumber": round_number,
                "prUrl": pr_url,
                "githubUsername": submission_data.get("githubUsername"),
                "repoOwner": self.repo_owner,
                "repoName": self.repo_name,
                "stakingKey": submission_data.get("stakingKey"),
                "pubKey": submission_data.get("pubKey"),
                "uuid": submission_data.get("uuid"),
                "nodeType": submission_data.get("nodeType"),
            },
            "submitterSignature": submission_data.get("signature"),
            "submitterStakingKey": submission_data.get("stakingKey"),
            "submitterPubKey": submission_data.get("pubKey"),
            "stakingKey": auditor_signatures["staking_key"],
            "pubKey": auditor_signatures["pub_key"],
            "stakingSignature": auditor_signatures["staking_signature"],
            "publicSignature": auditor_signatures["public_signature"],
            "prUrl": pr_url,
            "repoOwner": self.repo_owner,
            "repoName": self.repo_name,
            "githubUsername": os.getenv(f"{auditor.upper()}_GITHUB_USERNAME"),
        }

    def get_keys(self, role: str) -> Dict[str, str]:
        """Get the staking and public keys for a given role."""
        try:
            keypair = self.keypairs[role]
            staking_keypair_path = keypair["staking"]
            public_keypair_path = keypair["public"]

            if not staking_keypair_path or not public_keypair_path:
                return {
                    "staking_key": "dummy_staking_key",
                    "pub_key": "dummy_pub_key",
                }

            # Load keypairs
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
