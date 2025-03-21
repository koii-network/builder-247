import os
import requests
import json
import base58
import subprocess
import time
import signal
import argparse
import csv
from nacl.signing import SigningKey
from github import Github
from src.tools.github_operations.parser import extract_section
from dotenv import load_dotenv
import sys
import threading
from queue import Queue, Empty

# Load environment variables from .env file
load_dotenv()

# Define valid stages
VALID_STAGES = ["start", "worker-audit", "leader-task", "leader-audit"]


class TestState:
    def __init__(self, state_file="test_state.csv"):
        self.state_file = state_file
        self.pr_urls = {}
        self.load_state()

    def save_state(self):
        """Save current state to CSV file"""
        with open(self.state_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["role", "pr_url"])  # Header
            for role, url in self.pr_urls.items():
                writer.writerow([role, url])

    def load_state(self):
        """Load state from CSV file if it exists"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, "r", newline="") as f:
                    reader = csv.DictReader(f)
                    self.pr_urls = {row["role"]: row["pr_url"] for row in reader}
            else:
                self.pr_urls = {}
        except Exception as e:
            print(f"Warning: Failed to load state: {e}")
            self.pr_urls = {}

    def store_pr_url(self, key: str, url: str):
        """Store a PR URL"""
        self.pr_urls[key] = url
        self.save_state()

    def get_pr_url(self, key: str) -> str:
        """Get a stored PR URL"""
        return self.pr_urls.get(key)

    def clear_state(self):
        """Clear all stored state"""
        self.pr_urls = {}
        if os.path.exists(self.state_file):
            os.remove(self.state_file)


def log_request(method: str, url: str, payload: dict = None):
    """Log request details"""
    print("\n" + "=" * 80)
    print(f"REQUEST: {method} {url}")
    print("-" * 80)
    if payload:
        print("Payload:")
        print(json.dumps(payload, indent=2))
    print("-" * 80)


def log_response(response):
    """Log response details"""
    print("\nRESPONSE:")
    print("-" * 80)
    print(f"Status: {response.status_code}")
    try:
        print("Body:")
        print(json.dumps(response.json(), indent=2))
    except json.JSONDecodeError:
        print(f"Raw response: {response.text}")
    print("=" * 80)


def log_step(step_number: int, description: str):
    """Log a test step with clear formatting"""
    print("\n" + "#" * 80)
    print(f"STEP {step_number}: {description}")
    print("#" * 80)


def enqueue_output(out, queue):
    """Add output lines to queue"""
    for line in iter(out.readline, b""):
        queue.put(line)
    out.close()


class ServerInstance:
    def __init__(self, role: str, port: int, github_token: str, github_username: str):
        self.role = role
        self.port = port
        self.url = f"http://localhost:{port}"
        self.process = None
        self.stdout_queue = Queue()
        self.stderr_queue = Queue()
        self.stdout_thread = None
        self.stderr_thread = None
        self.output_thread = None
        self.github_username = github_username

        # Get the absolute path to the agents/builder directory
        self.builder_path = "/home/laura/git/github/builder-247/agents/builder"

        # Create unique database path for each server instance
        self.db_path = os.path.join(self.builder_path, f"database_{role}.db")

        # Set up environment
        self.env = os.environ.copy()
        self.env.update(
            {
                "GITHUB_TOKEN": github_token,
                "GITHUB_USERNAME": github_username,
                "PORT": str(port),
                "PYTHONPATH": self.builder_path,
                "DATABASE_PATH": self.db_path,  # Set unique database path
            }
        )

    def _read_output(self):
        """Read and print output from queues"""
        while self.process and self.process.poll() is None:
            # Check stdout
            try:
                line = self.stdout_queue.get_nowait()
                print(f"[{self.role}] {line.strip()}")
            except Empty:
                pass

            # Check stderr
            try:
                line = self.stderr_queue.get_nowait()
                print(f"[{self.role} ERR] {line.strip()}")
            except Empty:
                pass

            # Shorter sleep to be more responsive to output
            time.sleep(0.05)

    def start(self):
        """Start the Flask server instance"""
        print(f"\nStarting {self.role} server on port {self.port}...")

        # Set PYTHONUNBUFFERED=1 in the environment to force unbuffered output
        env = self.env.copy()
        env["PYTHONUNBUFFERED"] = "1"

        self.process = subprocess.Popen(
            [sys.executable, os.path.join(self.builder_path, "main.py")],
            env=env,
            cwd=self.builder_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,  # Line buffering
            universal_newlines=True,  # Use text mode for line buffering to work
        )

        # Start threads to read stdout and stderr
        self.stdout_thread = threading.Thread(
            target=enqueue_output, args=(self.process.stdout, self.stdout_queue)
        )
        self.stderr_thread = threading.Thread(
            target=enqueue_output, args=(self.process.stderr, self.stderr_queue)
        )
        self.stdout_thread.daemon = True
        self.stderr_thread.daemon = True
        self.stdout_thread.start()
        self.stderr_thread.start()

        # Start thread to read and print output
        self.output_thread = threading.Thread(target=self._read_output)
        self.output_thread.daemon = True
        self.output_thread.start()

        # Wait longer for server to start and logs to stabilize
        time.sleep(3)

        # Check if server started successfully
        if self.process.poll() is not None:
            # Process exited early - print error
            raise RuntimeError(f"Failed to start {self.role} server")

    def stop(self):
        """Stop the Flask server instance"""
        if self.process:
            print(f"\nStopping {self.role} server...")
            os.kill(self.process.pid, signal.SIGTERM)
            self.process = None


class EndpointTester:
    def __init__(self, start_stage="start"):
        # Check required environment variables
        required_env_vars = [
            "TASK_ID",  # Add TASK_ID to required env vars
            "WORKER1_STAKING_KEYPAIR",  # Keypair for worker1
            "WORKER1_PUBLIC_KEYPAIR",
            "WORKER2_STAKING_KEYPAIR",  # Keypair for worker2
            "WORKER2_PUBLIC_KEYPAIR",
            "LEADER_STAKING_KEYPAIR",  # Keypair for leader
            "LEADER_PUBLIC_KEYPAIR",
            "LEADER_GITHUB_TOKEN",
            "LEADER_GITHUB_USERNAME",
            "WORKER1_GITHUB_TOKEN",
            "WORKER1_GITHUB_USERNAME",
            "WORKER2_GITHUB_TOKEN",
            "WORKER2_GITHUB_USERNAME",
        ]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        self.task_id = os.getenv("TASK_ID")  # Get task ID from environment
        self.start_stage = start_stage
        self.state = TestState()  # Initialize state storage
        print(f"\nInitializing test sequence with TASK_ID: {self.task_id}")
        print(f"Starting from stage: {self.start_stage}")
        self.source_owner = "koii-network"
        self.source_repo = "builder-test"
        self.current_github_username = None  # Track current GitHub username
        self.current_role = None  # Track current role

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

        # Initialize server instances
        self.leader_server = ServerInstance(
            "leader",
            5000,
            os.getenv("LEADER_GITHUB_TOKEN"),
            os.getenv("LEADER_GITHUB_USERNAME"),
        )

        self.worker1_server = ServerInstance(
            "worker1",
            5001,
            os.getenv("WORKER1_GITHUB_TOKEN"),
            os.getenv("WORKER1_GITHUB_USERNAME"),
        )

        self.worker2_server = ServerInstance(
            "worker2",
            5002,
            os.getenv("WORKER2_GITHUB_TOKEN"),
            os.getenv("WORKER2_GITHUB_USERNAME"),
        )

        self.current_server = None

    def __enter__(self):
        """Start all server instances"""
        print("Starting server instances...")
        try:
            self.leader_server.start()
            self.worker1_server.start()
            self.worker2_server.start()
            return self
        except Exception as e:
            print(f"Failed to start servers: {str(e)}")
            # Clean up any started servers
            self.__exit__()
            raise

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        """Stop all server instances"""
        print("Stopping server instances...")
        if hasattr(self, "leader_server"):
            self.leader_server.stop()
        if hasattr(self, "worker1_server"):
            self.worker1_server.stop()
        if hasattr(self, "worker2_server"):
            self.worker2_server.stop()

    def _load_keypair(self, keypair_path):
        """Load a keypair from file and return signing key and public key."""
        with open(keypair_path) as f:
            keypair_bytes = bytes(json.load(f))
            private_key = keypair_bytes[:32]
            signing_key = SigningKey(private_key)
            verify_key = signing_key.verify_key
            public_key = base58.b58encode(bytes(verify_key)).decode("utf-8")
            return signing_key, public_key

    def switch_role(self, role: str):
        """Switch between leader/worker1/worker2 servers"""
        if role == "leader":
            self.current_server = self.leader_server
            self.current_github_username = os.getenv("LEADER_GITHUB_USERNAME")
        elif role == "worker1":
            self.current_server = self.worker1_server
            self.current_github_username = os.getenv("WORKER1_GITHUB_USERNAME")
        elif role == "worker2":
            self.current_server = self.worker2_server
            self.current_github_username = os.getenv("WORKER2_GITHUB_USERNAME")
        else:
            raise ValueError(f"Unknown role: {role}")
        self.current_role = role

    def create_signature(self, payload):
        """Create test signatures for a payload using test keypairs."""
        try:
            # Get keypair paths for current role
            if not self.current_role:
                raise ValueError("No role selected - call switch_role first")

            keypair = self.keypairs[self.current_role]
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

            print("\nDebug - Input Payload:")
            print(json.dumps(payload, indent=2))

            # Only add required fields if not already present
            if "pubKey" not in payload:
                payload["pubKey"] = pub_key
            if "stakingKey" not in payload:
                payload["stakingKey"] = staking_key
            if "githubUsername" not in payload:
                payload["githubUsername"] = self.current_github_username

            # Convert payload to string with sorted keys
            payload_str = json.dumps(payload, sort_keys=True).encode()

            print("\nDebug - Final Payload to Sign:")
            print(json.dumps(json.loads(payload_str), indent=2))

            # Create signatures
            staking_signed = staking_signing_key.sign(payload_str)
            public_signed = public_signing_key.sign(payload_str)

            print("\nDebug - Signature Details:")
            print(f"Payload length: {len(payload_str)} bytes")
            print(f"Staking signature length: {len(staking_signed.signature)} bytes")
            print(f"Public signature length: {len(public_signed.signature)} bytes")

            # Combine signatures with payload (signature first)
            staking_combined = staking_signed.signature + payload_str
            public_combined = public_signed.signature + payload_str

            # Encode combined data
            staking_signature = base58.b58encode(staking_combined).decode()
            public_signature = base58.b58encode(public_combined).decode()

            print("\nDebug - Combined Data:")
            print(f"Staking combined length: {len(staking_combined)} bytes")
            print(f"Public combined length: {len(public_combined)} bytes")
            print(f"Staking signature (base58): {staking_signature[:64]}...")
            print(f"Public signature (base58): {public_signature[:64]}...")

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

    def extract_staking_key_from_pr(self, pr_url: str) -> str:
        """Extract staking key from PR description"""
        # Get PR description using GitHub API
        parts = pr_url.strip("/").split("/")
        pr_number = int(parts[-1])
        pr_repo_owner = parts[-4]
        pr_repo_name = parts[-3]

        gh = Github(os.environ.get("GITHUB_TOKEN"))
        repo = gh.get_repo(f"{pr_repo_owner}/{pr_repo_name}")
        pr = repo.get_pull(pr_number)

        # Extract staking key section
        staking_section = extract_section(pr.body, "STAKING_KEY")
        if not staking_section:
            raise ValueError(f"No staking key found in PR {pr_url}")

        # Parse key from section (format: "key: signature")
        staking_key = staking_section.split(":")[0].strip()
        return staking_key

    def create_distribution_list(self, pr_urls: list, round_number: int):
        """Create distribution list from PR URLs"""
        distribution_list = {}
        for pr_url in pr_urls:
            worker_key = self.extract_staking_key_from_pr(pr_url)
            # Store full payload data for each worker
            distribution_list[worker_key] = {
                "taskId": self.task_id,
                "roundNumber": round_number - 3,  # Worker round is 3 rounds before
                "prUrl": pr_url,
                "stakingKey": worker_key,
            }
        return distribution_list

    def create_aggregator_repo(self, round_number: int):
        """Create aggregator repo using leader server"""
        print(f"\nCreating aggregator repo for round {round_number}...")
        self.switch_role("leader")

        payload = {
            "taskId": self.task_id,
            "repoOwner": self.source_owner,
            "repoName": self.source_repo,
        }
        url = f"{self.current_server.url}/create-aggregator-repo/{round_number}"

        log_request("POST", url, payload)
        response = requests.post(url, json=payload)
        log_response(response)

        result = response.json()
        if not result.get("success"):
            raise Exception(
                f"Failed to create aggregator repo: {result.get('message')}"
            )

        return result

    def run_worker_task(self, worker: str, round_number: int):
        """Run worker task endpoint"""
        print(f"\nRunning worker task for {worker} in round {round_number}...")
        self.switch_role(worker)

        # Create signature for worker task
        task_signatures = self.create_signature(
            {
                "taskId": self.task_id,
                "roundNumber": round_number,
                "action": "task",
            }
        )

        # Create payload matching task implementation
        leader_username = os.getenv("LEADER_GITHUB_USERNAME")
        payload = {
            "taskId": self.task_id,
            "roundNumber": round_number,
            "stakingKey": task_signatures["staking_key"],
            "pubKey": task_signatures["pub_key"],
            "stakingSignature": task_signatures["staking_signature"],
            "publicSignature": task_signatures["public_signature"],
            "repoOwner": leader_username,
            "repoName": self.source_repo,
            "distributionList": {},
        }

        print(f"\nSubmitting worker task for {worker}...")
        log_request(
            "POST", f"{self.current_server.url}/worker-task/{round_number}", payload
        )
        response = requests.post(
            f"{self.current_server.url}/worker-task/{round_number}", json=payload
        )
        log_response(response)

        result = response.json()
        if not result.get("success"):
            raise Exception(
                f"Worker task failed: {result.get('message', 'Unknown error')}"
            )

        pr_url = result.get("pr_url")
        if not pr_url:
            raise Exception("No PR URL returned from worker task")

        return pr_url

    def run_worker_audit(self, auditor: str, pr_url: str, round_number: int):
        """Run worker audit endpoint"""
        self.switch_role(auditor)

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

        # Create submission payload like in 2-submission.ts
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

        # Sign submission with submitter's keypair
        # Find the submitter's role by matching staking key
        submitter_role = None
        for role, keypairs in self.keypairs.items():
            staking_signing_key, staking_key = self._load_keypair(keypairs["staking"])
            if staking_key == submitter_key:
                submitter_role = role
                break

        if not submitter_role:
            raise ValueError(
                f"Could not find keypair for submitter staking key {submitter_key}"
            )

        # Create submitter's signature using their keypair
        submitter_keypair = self.keypairs[submitter_role]
        staking_signing_key, _ = self._load_keypair(submitter_keypair["staking"])

        # Sign the submission payload
        payload_str = json.dumps(submission_payload, sort_keys=True).encode()
        submitter_signed = staking_signing_key.sign(payload_str)
        submitter_signature = base58.b58encode(
            submitter_signed.signature + payload_str
        ).decode()

        # Now create auditor's signature
        signatures = self.create_signature(
            {
                "taskId": self.task_id,
                "roundNumber": round_number,
                "action": "audit",
                "githubUsername": pr.user.login,
                "prUrl": pr_url,
            }
        )

        # Create full payload matching 3-audit.ts podCallBody
        payload = {
            "submission": submission_payload,
            "submitterSignature": submitter_signature,
            "submitterStakingKey": submitter_key,
            "submitterPubKey": submitter_pub_key,
            "stakingKey": signatures["staking_key"],
            "pubKey": signatures["pub_key"],
            "stakingSignature": signatures["staking_signature"],
            "publicSignature": signatures["public_signature"],
        }

        log_request(
            "POST", f"{self.current_server.url}/worker-audit/{round_number}", payload
        )
        response = requests.post(
            f"{self.current_server.url}/worker-audit/{round_number}",
            json=payload,
        )
        log_response(response)

        # Handle API errors first
        if response.status_code >= 400:
            raise Exception(
                f"Worker audit API call failed with status {response.status_code}: {response.text}"
            )

        # Handle both boolean and JSON responses
        try:
            result = response.json()
            # If result is boolean, convert to standard format
            if isinstance(result, bool):
                result = {
                    "success": True,  # API call succeeded
                    "data": {"passed": result},  # Audit result
                }
        except json.JSONDecodeError:
            # If response is not JSON, assume it's a boolean string
            passed = response.text.strip().lower() == "true"
            result = {
                "success": True,  # API call succeeded
                "data": {"passed": passed},  # Audit result
            }

        # Check if API call was successful
        if not result.get("success"):
            raise Exception(
                f"Worker audit API call failed: {result.get('message', 'Unknown error')}"
            )

        # Check if audit passed
        if not result.get("data", {}).get("passed"):
            print(f"⚠️  Worker {auditor} rejected PR {pr_url}")
            raise Exception("Audit validation failed - PR was rejected")

        return result

    def run_leader_task(self, pr_urls: list, round_number: int):
        """Run leader task endpoint"""
        self.switch_role("leader")

        # Create signature first since we need the keys
        signatures = self.create_signature(
            {
                "taskId": self.task_id,
                "roundNumber": round_number,
                "action": "task",
            }
        )

        # Create distribution list from PR URLs - store full payload data
        distribution_list = self.create_distribution_list(pr_urls, round_number)

        # Create payload matching task implementation
        payload = {
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

        log_request(
            "POST", f"{self.current_server.url}/leader-task/{round_number}", payload
        )
        response = requests.post(
            f"{self.current_server.url}/leader-task/{round_number}", json=payload
        )
        log_response(response)

        result = response.json()
        if not result.get("success"):
            raise Exception(
                f"Leader task failed: {result.get('message', 'Unknown error')}"
            )

        pr_url = result.get("pr_url")
        if not pr_url:
            raise Exception("No PR URL returned from leader task")

        return pr_url

    def run_leader_audit(self, pr_url: str, round_number: int):
        """Run leader audit endpoint"""
        # Switch to worker1 for first audit, worker2 for second
        # This matches the pattern in run_worker_audit where workers cross-audit each other
        auditor = "worker1" if not hasattr(self, "_last_leader_auditor") else "worker2"
        self._last_leader_auditor = auditor
        self.switch_role(auditor)

        # Get PR info using GitHub API
        parts = pr_url.strip("/").split("/")
        pr_number = int(parts[-1])
        pr_repo_owner = parts[-4]
        pr_repo_name = parts[-3]

        gh = Github(os.getenv("GITHUB_TOKEN"))
        repo = gh.get_repo(f"{pr_repo_owner}/{pr_repo_name}")
        pr = repo.get_pull(pr_number)

        # Extract leader's keys from PR
        staking_section = extract_section(pr.body, "STAKING_KEY")
        if not staking_section:
            raise ValueError(f"No staking key found in PR {pr_url}")
        leader_key = staking_section.split(":")[0].strip()
        leader_signature = staking_section.split(":")[1].strip()

        pub_section = extract_section(pr.body, "PUB_KEY")
        if not pub_section:
            raise ValueError(f"No public key found in PR {pr_url}")
        leader_pub_key = pub_section.split(":")[0].strip()

        # Create distribution list from worker PRs
        worker_pr_urls = [
            self.state.get_pr_url("worker1"),
            self.state.get_pr_url("worker2"),
        ]
        distribution_list = self.create_distribution_list(worker_pr_urls, round_number)

        # Create submission data like in 3-audit.ts
        submission_data = {
            "taskId": self.task_id,
            "roundNumber": round_number,
            "prUrl": pr_url,
            "repoOwner": pr_repo_owner,
            "repoName": pr_repo_name,
            "stakingKey": leader_key,
            "pubKey": leader_pub_key,
            "signature": leader_signature,  # Add leader's signature
            "action": "audit",
            "githubUsername": pr.user.login,
            "distributionList": distribution_list,
            "leaders": [leader_key],  # Add leaders array with leader's key
        }

        # Create auditor's signatures
        signatures = self.create_signature(submission_data)

        # Create full payload matching 3-audit.ts PodCallBody interface
        payload = {
            "submission": submission_data,
            "submitterSignature": leader_signature,
            "submitterStakingKey": leader_key,
            "submitterPubKey": leader_pub_key,
            "prUrl": pr_url,
            "repoOwner": pr_repo_owner,
            "repoName": pr_repo_name,
            "githubUsername": pr.user.login,
            "stakingKey": signatures["staking_key"],
            "pubKey": signatures["pub_key"],
            "stakingSignature": signatures["staking_signature"],
            "publicSignature": signatures["public_signature"],
            "distributionList": distribution_list,
        }

        log_request(
            "POST", f"{self.current_server.url}/leader-audit/{round_number}", payload
        )
        response = requests.post(
            f"{self.current_server.url}/leader-audit/{round_number}",
            json=payload,
        )
        log_response(response)

        result = response.json()
        if not result.get("success"):
            raise Exception(
                f"Leader audit failed: {result.get('message', 'Unknown error')}"
            )

        return result

    def run_test_sequence(self):
        """Run the full test sequence"""
        try:
            pr1_url = self.state.get_pr_url("worker1")
            pr2_url = self.state.get_pr_url("worker2")
            leader_pr_url = self.state.get_pr_url("leader")

            if self.start_stage == "start":
                # 1. Create aggregator repo
                log_step(1, "Creating aggregator repo")
                result = self.create_aggregator_repo(1)
                if not result.get("success"):
                    raise Exception(
                        f"Failed to create aggregator repo: {result.get('message')}"
                    )
                print("✓ Aggregator repo created successfully")

                # 2. Worker 1 task
                log_step(2, "Running Worker 1 task")
                pr1_url = self.run_worker_task("worker1", 1)
                if not pr1_url:
                    raise Exception("Worker 1 task failed - no PR URL returned")
                self.state.store_pr_url("worker1", pr1_url)
                print(f"✓ Worker 1 PR created: {pr1_url}")

                # 3. Worker 2 task
                log_step(3, "Running Worker 2 task")
                pr2_url = self.run_worker_task("worker2", 1)
                if not pr2_url:
                    raise Exception("Worker 2 task failed - no PR URL returned")
                self.state.store_pr_url("worker2", pr2_url)
                print(f"✓ Worker 2 PR created: {pr2_url}")

            if self.start_stage in ["start", "worker-audit"]:
                # 4. Cross audits
                log_step(4, "Running cross audits")
                if not pr1_url or not pr2_url:
                    raise Exception("Missing worker PR URLs for cross audits")

                print("\nWorker 2 auditing Worker 1's PR...")
                audit1_result = self.run_worker_audit("worker2", pr1_url, 1)
                if not audit1_result.get("success"):
                    raise Exception(
                        f"Worker 2 audit failed: {audit1_result.get('message')}"
                    )
                print("✓ Worker 2 audit complete")

                print("\nWorker 1 auditing Worker 2's PR...")
                audit2_result = self.run_worker_audit("worker1", pr2_url, 1)
                if not audit2_result.get("success"):
                    raise Exception(
                        f"Worker 1 audit failed: {audit2_result.get('message')}"
                    )
                print("✓ Worker 1 audit complete")

            if self.start_stage in ["start", "worker-audit", "leader-task"]:
                # 5. Leader task
                log_step(5, "Running leader task")
                if not pr1_url or not pr2_url:
                    raise Exception("Missing worker PR URLs for leader task")

                leader_pr_url = self.run_leader_task([pr1_url, pr2_url], 4)
                if not leader_pr_url:
                    raise Exception("Leader task failed - no PR URL returned")
                self.state.store_pr_url("leader", leader_pr_url)
                print(f"✓ Leader PR created: {leader_pr_url}")

            if self.start_stage in [
                "start",
                "worker-audit",
                "leader-task",
                "leader-audit",
            ]:
                # 6. Leader audits
                log_step(6, "Running leader audits")
                if not leader_pr_url:
                    raise Exception("Missing leader PR URL for leader audits")

                print("\nFirst leader audit...")
                audit3_result = self.run_leader_audit(leader_pr_url, 4)
                if not audit3_result.get("success"):
                    raise Exception(
                        f"First leader audit failed: {audit3_result.get('message')}"
                    )
                print("✓ First leader audit complete")

                # print("\nSecond leader audit...")
                # audit4_result = self.run_leader_audit(leader_pr_url, 4)
                # if not audit4_result.get("success"):
                #     raise Exception(
                #         f"Second leader audit failed: {audit4_result.get('message')}"
                #     )
                # print("✓ Second leader audit complete")

            print("\n" + "=" * 80)
            print("TEST SEQUENCE COMPLETED SUCCESSFULLY")
            print("=" * 80)

        except Exception as e:
            print("\n" + "!" * 80)
            print(f"TEST SEQUENCE FAILED: {str(e)}")
            print("!" * 80)
            raise


def main():
    parser = argparse.ArgumentParser(description="Run test sequence for builder task")
    parser.add_argument(
        "--stage",
        type=str,
        choices=VALID_STAGES,
        default="start",
        help="Stage to start from (default: start)",
    )
    parser.add_argument(
        "--clear-state", action="store_true", help="Clear stored state before running"
    )
    args = parser.parse_args()

    try:
        with EndpointTester(start_stage=args.stage) as tester:
            if args.clear_state:
                tester.state.clear_state()
            tester.run_test_sequence()
    except Exception as e:
        print(f"Test sequence failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
