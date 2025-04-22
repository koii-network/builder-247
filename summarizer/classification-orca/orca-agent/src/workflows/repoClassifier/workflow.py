"""Task decomposition workflow implementation."""

import os
import contextlib
from github import Github
from prometheus_swarm.workflows.base import Workflow
from prometheus_swarm.utils.logging import log_section, log_key_value, log_error
from src.workflows.repoClassifier import phases
from prometheus_swarm.workflows.utils import (
    check_required_env_vars,
    cleanup_repository,
    validate_github_auth,
    setup_repository
)
from src.workflows.repoClassifier.prompts import PROMPTS


class Task:
    def __init__(self, title: str, description: str, acceptance_criteria: list[str]):
        self.title = title
        self.description = description
        self.acceptance_criteria = acceptance_criteria

    def to_dict(self) -> dict:
        """Convert task to dictionary format."""
        return {
            "title": self.title,
            "description": self.description,
            "acceptance_criteria": self.acceptance_criteria,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create task from dictionary."""
        return cls(
            title=data["title"],
            description=data["description"],
            acceptance_criteria=data["acceptance_criteria"],
        )


class RepoClassifierWorkflow(Workflow):
    def __init__(
        self,
        client,
        prompts,
        repo_url,
    ):
        # Extract owner and repo name from URL
        # URL format: https://github.com/owner/repo
        parts = repo_url.strip("/").split("/")
        repo_owner = parts[-2]
        repo_name = parts[-1]

        super().__init__(
            client=client,
            prompts=prompts,
            repo_url=repo_url,
            repo_owner=repo_owner,
            repo_name=repo_name,
        )
        self._cleanup_required = False

    @contextlib.contextmanager
    def managed_workflow(self):
        """Context manager to ensure proper cleanup."""
        try:
            self.setup()
            self._cleanup_required = True
            yield self
        except Exception as e:
            log_error(e, "Error during workflow execution")
            raise
        finally:
            if self._cleanup_required:
                self.cleanup()

    def setup(self):
        try:
            """Set up repository and workspace."""
            check_required_env_vars(["GITHUB_TOKEN", "GITHUB_USERNAME"])
            validate_github_auth(os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_USERNAME"))

            # Get the default branch from GitHub
            try:
                gh = Github(os.getenv("GITHUB_TOKEN"))
                self.context["repo_full_name"] = (
                    f"{self.context['repo_owner']}/{self.context['repo_name']}"
                )

                repo = gh.get_repo(
                    f"{self.context['repo_owner']}/{self.context['repo_name']}"
                )
                self.context["base"] = repo.default_branch
                log_key_value("Default branch", self.context["base"])
            except Exception as e:
                log_error(e, "Failed to get default branch, using 'main'")
                self.context["base"] = "main" 
                

            # Set up repository directory
            setup_result = setup_repository(self.context["repo_url"], github_token=os.getenv("GITHUB_TOKEN"), github_username=os.getenv("GITHUB_USERNAME"))
            if not setup_result["success"]:
                raise Exception(f"Failed to set up repository: {setup_result['message']}")
            self.context["github_token"] = os.getenv("GITHUB_TOKEN")
            self.context["repo_path"] = setup_result["data"]["clone_path"]
            self.original_dir = setup_result["data"]["original_dir"]
            self.context["fork_url"] = setup_result["data"]["fork_url"]
            self.context["fork_owner"] = setup_result["data"]["fork_owner"]
            self.context["fork_name"] = setup_result["data"]["fork_name"]

            # Enter repo directory
            os.chdir(self.context["repo_path"])
        except Exception as e:
            log_error(e, "Error during setup")
            raise
        # Configure Git user info
        # setup_git_user_config(self.context["repo_path"])

        # Get current files for context

    def cleanup(self):
        """Cleanup workspace."""
        try:
            # Make sure we're not in the repo directory before cleaning up
            if os.getcwd() == self.context.get("repo_path", ""):
                os.chdir(self.original_dir)
            
            log_key_value("Cleaning up repository", self.context.get("repo_path", ""))
            
            # Clean up the repository directory
            if self.context.get("repo_path"):
                cleanup_repository(self.original_dir, self.context["repo_path"])
            
            # Clean up any temporary files or resources
            self._cleanup_temporary_resources()
            
            # Reset cleanup flag
            self._cleanup_required = False
            
        except Exception as e:
            log_error(e, "Error during cleanup")
            # Don't raise the exception to ensure cleanup continues
            pass

    def _cleanup_temporary_resources(self):
        """Clean up any temporary resources created during workflow execution."""
        # Add any additional cleanup steps here
        pass

    def run(self):
        with self.managed_workflow():
            repoMetadata = {}
            max_retries = 3
            
            # Helper function to extract pure string from classification result
            def extract_value(result, key):
                if result.get("success") and result.get("data", {}).get(key):
                    return result["data"][key]
                return None
            
            # Helper function to retry classification
            def retry_classification(phase_class, retries=max_retries):
                for attempt in range(retries):
                    try:
                        result = phase_class(self).execute()
                        if result.get("success"):
                            return result
                        if attempt < retries - 1:
                            log_error(f"Attempt {attempt + 1} failed, retrying...")
                    except Exception as e:
                        log_error(e, f"Error during classification attempt {attempt + 1}")
                        if attempt == retries - 1:
                            raise
                return result
            
            try:
                # Get repository type with retry
                repo_type_result = retry_classification(phases.RepoClassificationPhase)
                repoMetadata["repo_type"] = extract_value(repo_type_result, "repo_type")
                
                # Get language with retry
                language_result = retry_classification(phases.LanguageClassificationPhase)
                repoMetadata["language"] = extract_value(language_result, "language")
                
                # Get test framework with retry
                test_framework_result = retry_classification(phases.TestFrameworkClassificationPhase)
                repoMetadata["test_framework"] = extract_value(test_framework_result, "test_framework")
                
                # Check if all classifications were successful
                success = all([
                    repoMetadata["repo_type"],
                    repoMetadata["language"],
                    repoMetadata["test_framework"]
                ])
                
                log_key_value("Repository metadata", repoMetadata)
                
                return {
                    "success": success,
                    "message": "Repository classification complete" if success else "Repository classification failed",
                    "data": repoMetadata,
                }
                
            except Exception as e:
                log_error(e, "Error during repository classification")
                raise
    
    