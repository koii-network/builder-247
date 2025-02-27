"""Task workflow implementation using new workflow structure."""

import os
import shutil
from git import Repo
import ast
import time
from src.workflows.base import Workflow
from src.tools.file_operations.implementations import list_files
from src.tools.github_operations.implementations import fork_repository
from src.utils.logging import log_section, log_key_value, log_error
from src.workflows.task import phases


class TaskWorkflow(Workflow):
    def __init__(
        self,
        client,
        system_prompt,
        repo_owner,
        repo_name,
        todo,
        acceptance_criteria,
    ):
        super().__init__(
            client,
            system_prompt,
            repo_owner=repo_owner,
            repo_name=repo_name,
            todo=todo,
            acceptance_criteria=acceptance_criteria,
            files_directory=None,
        )

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

        # Fork and clone repository
        log_section("FORKING AND CLONING REPOSITORY")
        fork_result = fork_repository(
            f"{self.repo_owner}/{self.repo_name}", self.context["repo_path"]
        )
        if not fork_result["success"]:
            error = fork_result.get("error", "Unknown error")
            log_error(Exception(error), "Fork failed")
            raise Exception(error)

        # Enter repo directory
        self.original_dir = os.getcwd()
        os.chdir(self.context["repo_path"])

        # Configure Git user info
        repo = Repo(self.context["repo_path"])
        with repo.config_writer() as config:
            config.set_value("user", "name", os.environ["GITHUB_USERNAME"])
            config.set_value(
                "user",
                "email",
                f"{os.environ['GITHUB_USERNAME']}@users.noreply.github.com",
            )
        self.context["files_directory"] = self._get_current_files()

    def cleanup(self):
        """Cleanup workspace."""
        os.chdir(self.original_dir)
        if os.path.exists(self.context["repo_path"]):
            shutil.rmtree(self.context["repo_path"])

    def _get_current_files(self):
        """Get current files in repository."""
        files_result = list_files(".")
        if not files_result["success"]:
            raise Exception(f"Failed to get file list: {files_result['message']}")

        return files_result["data"]["files"]

    def run(self):
        """Execute the task workflow."""
        try:
            self.setup()

            # Create main conversation
            conversation_id = self.client.create_conversation(
                system_prompt=self.system_prompt
            )

            # Create branch
            branch_phase = phases.BranchCreationPhase.create(workflow=self)
            branch_result = branch_phase.execute()

            if not branch_result:
                return None

            branch_data = ast.literal_eval(branch_result["response"])
            if not branch_data.get("success"):
                error = branch_data.get("error", "Unknown error")
                log_error(Exception(error), "Branch creation failed")
                return None

            self.context["branch_name"] = branch_data["data"]["branch_name"]

            # Implementation loop
            max_implementation_attempts = 3
            for attempt in range(max_implementation_attempts):
                log_section(
                    f"IMPLEMENTATION ATTEMPT {attempt + 1}/{max_implementation_attempts}"
                )

                # Get current files
                self.context["files_directory"] = self._get_current_files()

                # Run implementation
                phase = (
                    phases.ImplementationPhase
                    if attempt == 0
                    else phases.FixImplementationPhase
                )
                implementation_phase = phase.create(
                    workflow=self, conversation_id=branch_phase.conversation_id
                )
                implementation_result = implementation_phase.execute()

                print(implementation_result)

                # Validate
                validation_phase = phases.ValidationPhase.create(workflow=self)
                validation_result = validation_phase.execute()

                if not validation_result:
                    continue

                result_data = ast.literal_eval(validation_result["response"])
                if not result_data.get("success"):
                    self.context["validation_message"] = result_data.get(
                        "error", "Unknown error"
                    )
                    continue

                validation_data = result_data.get("data", {})
                if validation_data.get("validated", False):
                    break

                if attempt == max_implementation_attempts - 1:
                    log_error(
                        Exception(self.context.get("validation_message")),
                        "Failed to meet acceptance criteria",
                    )
                    return None

                self.context["validation_message"] = "Failed validation"
                time.sleep(5)  # Brief pause before retry

            # Create PR
            self.context["files_directory"] = self._get_current_files()

            pr_phase = phases.PullRequestPhase.create(
                workflow=self, conversation_id=branch_phase.conversation_id
            )
            pr_result = pr_phase.execute()

            if not pr_result:
                return None

            pr_data = ast.literal_eval(pr_result["response"])
            if pr_data.get("success"):
                pr_url = pr_data.get("data", {}).get("pr_url")
                log_key_value("PR created successfully", pr_url)
                return pr_url
            else:
                log_error(Exception(pr_data.get("error")), "PR creation failed")
                return None

        except Exception as e:
            log_error(e, "Error in task workflow")
            raise

        finally:
            self.cleanup()
