import os
import sys
import subprocess
import time
import signal
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()


class ServerInstance:
    def __init__(self, role: str, port: int, github_token: str, github_username: str):
        self.role = role
        self.port = port
        self.url = f"http://localhost:{port}"
        self.process = None
        self.github_username = github_username

        # Get the absolute path to the builder directory
        self.builder_path = Path(__file__).parent.parent

        # Create unique database path for each server instance
        self.db_path = self.builder_path / f"database_{role}.db"

        # Set up environment
        self.env = os.environ.copy()
        self.env.update(
            {
                "GITHUB_TOKEN": github_token,
                "GITHUB_USERNAME": github_username,
                "PORT": str(port),
                "DATABASE_PATH": str(self.db_path),
                "PYTHONUNBUFFERED": "1",  # Force unbuffered output
            }
        )

    def _print_output(self, stream, prefix):
        """Print output from a stream with a prefix"""
        for line in stream:
            print(f"{prefix} {line.strip()}")
            sys.stdout.flush()

    def start(self):
        """Start the Flask server instance"""
        print(f"\nStarting {self.role} server on port {self.port}...")
        sys.stdout.flush()

        # Start the process with unbuffered output
        self.process = subprocess.Popen(
            [sys.executable, str(self.builder_path / "main.py")],
            env=self.env,
            cwd=self.builder_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True,
        )

        # Wait for server to start
        time.sleep(3)

        # Check if server started successfully
        if self.process.poll() is not None:
            _, stderr = self.process.communicate()
            error_msg = stderr.strip() if stderr else "No error output available"
            raise RuntimeError(f"Failed to start {self.role} server:\n{error_msg}")

        # Start threads to read and print output
        import threading

        stdout_thread = threading.Thread(
            target=self._print_output,
            args=(self.process.stdout, f"[{self.role}]"),
            daemon=True,
        )
        stderr_thread = threading.Thread(
            target=self._print_output,
            args=(self.process.stderr, f"[{self.role} ERR]"),
            daemon=True,
        )
        stdout_thread.start()
        stderr_thread.start()

    def stop(self):
        """Stop the Flask server instance"""
        if self.process:
            print(f"\nStopping {self.role} server...")
            sys.stdout.flush()

            # Send SIGTERM first to allow graceful shutdown
            os.kill(self.process.pid, signal.SIGTERM)
            time.sleep(1)

            # If still running, send SIGKILL
            if self.process.poll() is None:
                os.kill(self.process.pid, signal.SIGKILL)

            # Wait for process to fully terminate
            self.process.wait()
            self.process = None


class TestSetup:
    def __init__(self):
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
            self._cleanup_servers()
            raise

    def _cleanup_servers(self):
        """Clean up server processes safely"""
        for server in [self.leader_server, self.worker1_server, self.worker2_server]:
            if hasattr(server, "process") and server.process:
                try:
                    os.kill(server.process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass  # Process already gone
                server.process = None

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        """Stop all server instances"""
        print("Stopping server instances...")
        self._cleanup_servers()

    def switch_role(self, role: str):
        """Switch between leader/worker1/worker2 servers"""
        if role == "leader":
            self.current_server = self.leader_server
        elif role == "worker1":
            self.current_server = self.worker1_server
        elif role == "worker2":
            self.current_server = self.worker2_server
        else:
            raise ValueError(f"Unknown role: {role}")

    def create_aggregator_repo(self, data_manager):
        """Create aggregator repo and update aggregator info"""
        import requests

        self.switch_role("leader")
        payload = data_manager.prepare_create_aggregator_repo()

        url = f"{self.current_server.url}/create-aggregator-repo/{data_manager.task_id}"
        response = requests.post(url, json=payload)

        result = response.json()
        if not result.get("success"):
            raise Exception(
                f"Failed to create aggregator repo: {result.get('message')}"
            )

        # Store the fork URL and branch name for use in subsequent steps
        data_manager.fork_url = result.get("data", {}).get("fork_url")
        data_manager.branch_name = result.get("data", {}).get("branch_name")
        data_manager.issue_uuid = result.get("data", {}).get("issue_uuid")

        # Extract repository info from fork URL
        repo_parts = data_manager.fork_url.strip("/").split("/")
        if len(repo_parts) >= 2:
            data_manager.repo_owner = repo_parts[-2]
            data_manager.repo_name = repo_parts[-1]

        # Update aggregator info
        aggregator_payload = data_manager.prepare_aggregator_info(
            "leader", data_manager.round_number
        )
        url = f"{self.current_server.url}/add-aggregator-info/{data_manager.task_id}"
        response = requests.post(url, json=aggregator_payload)

        result = response.json()
        if not result.get("success"):
            raise Exception(f"Failed to add aggregator info: {result.get('message')}")

    def run_worker_task(self, data_manager, pr_urls):
        """Run worker tasks for both workers"""
        import requests

        # Worker 1 task
        self.switch_role("worker1")
        payload = data_manager.prepare_worker_task("worker1", data_manager.round_number)
        url = f"{self.current_server.url}/worker-task/{data_manager.round_number}"
        response = requests.post(url, json=payload)

        result = response.json()
        if not result.get("success"):
            raise Exception(f"Worker 1 task failed: {result.get('message')}")
        pr_urls["worker1"] = result.get("pr_url")

        # Worker 2 task
        self.switch_role("worker2")
        payload = data_manager.prepare_worker_task("worker2", data_manager.round_number)
        url = f"{self.current_server.url}/worker-task/{data_manager.round_number}"
        response = requests.post(url, json=payload)

        result = response.json()
        if not result.get("success"):
            raise Exception(f"Worker 2 task failed: {result.get('message')}")
        pr_urls["worker2"] = result.get("pr_url")

    def run_worker_audit(self, data_manager, pr_urls):
        """Run cross audits between workers"""
        import requests

        # Worker 2 audits Worker 1's PR
        self.switch_role("worker2")
        payload = data_manager.prepare_worker_audit(
            "worker2", pr_urls["worker1"], data_manager.round_number
        )
        url = f"{self.current_server.url}/worker-audit/{data_manager.round_number}"
        response = requests.post(url, json=payload)

        result = response.json()
        if not result.get("success"):
            raise Exception(f"Worker 2 audit failed: {result.get('message')}")

        # Worker 1 audits Worker 2's PR
        self.switch_role("worker1")
        payload = data_manager.prepare_worker_audit(
            "worker1", pr_urls["worker2"], data_manager.round_number
        )
        url = f"{self.current_server.url}/worker-audit/{data_manager.round_number}"
        response = requests.post(url, json=payload)

        result = response.json()
        if not result.get("success"):
            raise Exception(f"Worker 1 audit failed: {result.get('message')}")

    def update_audit_results(self, data_manager):
        """Update audit results based on the distribution list"""
        import requests
        import os

        self.switch_role("leader")
        update_payload = {
            "taskId": data_manager.task_id,
            "round": data_manager.round_number,
        }
        url = f"{os.getenv('MIDDLE_SERVER_URL')}/api/update-audit-result"
        response = requests.post(url, json=update_payload)

        result = response.json()
        if not result.get("success", False):
            raise Exception(
                f"Update audit result failed: {result.get('message', 'Unknown error')}"
            )
        print("✓ Audit results processed")

    def run_leader_task(self, data_manager, pr_urls):
        """Run leader task"""
        import requests

        # Leader task
        self.switch_role("leader")
        payload = data_manager.prepare_leader_task(
            "leader",
            data_manager.round_number,
            [pr_urls["worker1"], pr_urls["worker2"]],
        )
        url = f"{self.current_server.url}/leader-task/{data_manager.round_number}"
        response = requests.post(url, json=payload)

        result = response.json()
        if not result.get("success"):
            raise Exception(f"Leader task failed: {result.get('message')}")
        pr_urls["leader"] = result.get("pr_url")
        print(f"✓ Leader PR created: {pr_urls['leader']}")

    def run_leader_audit(self, data_manager, pr_urls):
        """Run leader audit"""

        # Leader audit
        self.switch_role("worker1")
        payload = data_manager.prepare_leader_audit(
            "worker1", pr_urls["leader"], data_manager.round_number
        )
        url = f"{self.current_server.url}/leader-audit/{data_manager.round_number}"
        response = requests.post(url, json=payload)

        result = response.json()
        if not result.get("success"):
            raise Exception(f"Leader audit failed: {result.get('message')}")
        print("✓ Leader PR audited")
