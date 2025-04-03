import os
import json
import base58
from nacl.signing import SigningKey
from typing import Dict, Any
from github import Github
from agent_framework.tools.github_operations.parser import extract_section


class DataManager:
    def __init__(self):
        self.task_id = os.getenv("TASK_ID")
        self.fork_url = None
        self.branch_name = None
        self.issue_uuid = None
        self.repo_owner = None
        self.repo_name = None

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

        # Extract aggregator owner from fork URL
        # Format typically: https://github.com/username/repo-name
        repo_parts = self.fork_url.strip("/").split("/")
        aggregator_owner = repo_parts[-2]

        # Extract repo name from fork URL if not set
        if not self.repo_name:
            self.repo_name = repo_parts[-1]
            print(f"Extracted repo name from fork URL: {self.repo_name}")

        # Create fetch-todo payload for stakingSignature and publicSignature
        fetch_todo_payload = {
            "taskId": self.task_id,
            "roundNumber": round_number,
            "action": "fetch-todo",
            "githubUsername": os.getenv(f"{role.upper()}_GITHUB_USERNAME"),
            "forkUrl": self.fork_url,
            "branchName": self.branch_name,
        }

        # Create add-pr payload for addPRSignature
        add_pr_payload = {
            "taskId": self.task_id,
            "roundNumber": round_number,
            "action": "add-pr",
            "githubUsername": os.getenv(f"{role.upper()}_GITHUB_USERNAME"),
            "forkUrl": self.fork_url,
            "branchName": self.branch_name,
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

        return {
            "taskId": self.task_id,
            "roundNumber": round_number,
            "stakingKey": fetch_signatures["staking_key"],
            "pubKey": fetch_signatures["pub_key"],
            "stakingSignature": fetch_signatures["staking_signature"],
            "publicSignature": fetch_signatures["public_signature"],
            "addPRSignature": add_pr_signature,  # Add the new signature
            "repoOwner": aggregator_owner,  # Use the aggregator owner
            "repoName": self.repo_name,  # Use repo name from fork URL or server response
            "distributionList": {},
            "forkUrl": self.fork_url,
            "branchName": self.branch_name,
        }

    def prepare_worker_audit(
        self, auditor: str, pr_url: str, round_number: int
    ) -> Dict[str, Any]:
        """Prepare payload for worker-audit endpoint."""
        # Get PR info using GitHub API
        parts = pr_url.strip("/").split("/")
        pr_number = int(parts[-1])
        pr_repo_owner = parts[-4]
        pr_repo_name = parts[-3]

        gh = Github(os.getenv("GITHUB_TOKEN"))
        repo = gh.get_repo(f"{pr_repo_owner}/{pr_repo_name}")
        pr = repo.get_pull(pr_number)

        # Extract submitter's keys from PR
        staking_section = extract_section(pr.body, "STAKING_KEY")
        if not staking_section:
            raise ValueError(f"No staking key found in PR {pr_url}")
        submitter_key = staking_section.split(":")[0].strip()

        pub_section = extract_section(pr.body, "PUB_KEY")
        if not pub_section:
            raise ValueError(f"No public key found in PR {pr_url}")
        submitter_pub_key = pub_section.split(":")[0].strip()

        # Create submission payload
        submission_payload = {
            "taskId": self.task_id,
            "roundNumber": round_number,
            "stakingKey": submitter_key,
            "pubKey": submitter_pub_key,
            "action": "audit",
            "githubUsername": pr.user.login,
            "prUrl": pr_url,
            "repoOwner": pr_repo_owner,
            "repoName": pr_repo_name,
        }

        # Create auditor's signatures
        signatures = self.create_signature(auditor, submission_payload)

        return {
            "submission": submission_payload,
            "submitterSignature": staking_section.split(":")[1].strip(),
            "submitterStakingKey": submitter_key,
            "submitterPubKey": submitter_pub_key,
            "prUrl": pr_url,
            "repoOwner": pr_repo_owner,
            "repoName": pr_repo_name,
            "githubUsername": pr.user.login,
            "stakingKey": signatures["staking_key"],
            "pubKey": signatures["pub_key"],
            "stakingSignature": signatures["staking_signature"],
            "publicSignature": signatures["public_signature"],
        }

    def prepare_leader_task(
        self, role: str, round_number: int, pr_urls: list[str]
    ) -> Dict[str, Any]:
        """Prepare payload for leader-task endpoint."""
        # Create distribution list from PR URLs
        distribution_list = {}
        for pr_url in pr_urls:
            worker_key = self.extract_staking_key_from_pr(pr_url)
            distribution_list[worker_key] = {
                "taskId": self.task_id,
                "roundNumber": round_number - 3,  # Worker round is 3 rounds before
                "prUrl": pr_url,
                "stakingKey": worker_key,
            }

        payload = {
            "taskId": self.task_id,
            "roundNumber": round_number,
            "action": "task",
            "githubUsername": os.getenv(f"{role.upper()}_GITHUB_USERNAME"),
        }

        signatures = self.create_signature(role, payload)

        return {
            "taskId": self.task_id,
            "roundNumber": round_number,
            "stakingKey": signatures["staking_key"],
            "pubKey": signatures["pub_key"],
            "stakingSignature": signatures["staking_signature"],
            "publicSignature": signatures["public_signature"],
            "repoOwner": os.getenv("LEADER_GITHUB_USERNAME"),
            "repoName": self.source_repo,
            "distributionList": distribution_list,
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
