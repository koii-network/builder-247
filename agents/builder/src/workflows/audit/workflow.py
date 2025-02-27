"""Audit workflow implementation using new workflow structure."""

import os
import shutil
from git import Repo
import ast
from github import Github

from src.workflows.base import Workflow, WorkflowPhase
from src.workflows.prompts import PROMPTS
from src.tools.file_operations.implementations import list_files
from src.utils.logging import log_section, log_key_value, log_error


class AuditWorkflow(Workflow):
    def __init__(self, client, system_prompt, repo_owner, repo_name, pr_number):
        super().__init__(client, system_prompt)
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.pr_number = pr_number
        self.context = {
            "repo_owner": repo_owner,
            "repo_name": repo_name,
            "pr_number": pr_number,
        }

    def setup(self):
        """Set up repository and workspace."""
        # Generate sequential repo path
        base_dir = os.path.abspath("./repos")
        os.makedirs(base_dir, exist_ok=True)

        counter = 0
        while True:
            candidate_path = os.path.join(base_dir, f"repo_{counter}")
            if not os.path.exists(candidate_path):
                self.context["repo_path"] = candidate_path
                break
            counter += 1

        # Clean existing repository
        if os.path.exists(self.context["repo_path"]):
            shutil.rmtree(self.context["repo_path"])

        # Create parent directory
        os.makedirs(os.path.dirname(self.context["repo_path"]), exist_ok=True)

        # Clone repository
        log_section("CLONING REPOSITORY")
        gh = Github(os.environ["GITHUB_TOKEN"])
        repo = gh.get_repo(f"{self.repo_owner}/{self.repo_name}")

        log_key_value("Cloning repository to", self.context["repo_path"])
        git_repo = Repo.clone_from(repo.clone_url, self.context["repo_path"])

        # Fetch PR
        log_key_value("Fetching PR", f"#{self.pr_number}")
        git_repo.remote().fetch(f"pull/{self.pr_number}/head:pr_{self.pr_number}")

        # Checkout PR branch
        log_key_value("Checking out PR branch", f"pr_{self.pr_number}")
        git_repo.git.checkout(f"pr_{self.pr_number}")

        # Enter repo directory
        self.original_dir = os.getcwd()
        os.chdir(self.context["repo_path"])

    def cleanup(self):
        """Cleanup workspace."""
        os.chdir(self.original_dir)
        if os.path.exists(self.context["repo_path"]):
            shutil.rmtree(self.context["repo_path"])

    def run(self):
        """Execute the audit workflow."""
        try:
            self.setup()

            # Get current files
            files_result = list_files(".")
            if not files_result["success"]:
                raise Exception(f"Failed to get file list: {files_result['message']}")

            files = files_result["data"]["files"]
            files_directory = ", ".join(map(str, files))

            # Define review phase
            review_phase = WorkflowPhase(
                prompt_template=PROMPTS["review_pr"], name="PR Review"
            )

            # Create conversation and run review
            conversation_id = self.client.create_conversation(
                system_prompt=self.system_prompt
            )

            review_result = self.run_phase(
                review_phase,
                conversation_id,
                pr_number=self.pr_number,
                repo=f"{self.repo_owner}/{self.repo_name}",
                files_list=files_directory,
            )

            if not review_result:
                return None

            result_data = ast.literal_eval(review_result["response"])
            if result_data.get("success"):
                log_key_value("Review completed", "PR reviewed successfully")
                return result_data.get("validated", False)
            else:
                log_error(Exception(result_data.get("error")), "Review failed")
                return None

        except Exception as e:
            log_error(e, "Error in audit workflow")
            raise

        finally:
            self.cleanup()
