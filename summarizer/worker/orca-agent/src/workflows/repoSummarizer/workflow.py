"""Task decomposition workflow implementation."""

import os
from github import Github
from prometheus_swarm.workflows.base import Workflow
from prometheus_swarm.utils.logging import log_section, log_key_value, log_error
from src.workflows.repoSummarizer import phases
from prometheus_swarm.workflows.utils import (
    check_required_env_vars,
    cleanup_repository,
    validate_github_auth,
    setup_repository,
)
from src.workflows.repoSummarizer.prompts import PROMPTS
from src.workflows.repoSummarizer.docs_sections import (
    DOCS_SECTIONS,
    INITIAL_SECTIONS,
    FINAL_SECTIONS,
)


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


class RepoSummarizerWorkflow(Workflow):
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

    def setup(self):
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
        setup_result = setup_repository(
            self.context["repo_url"],
            github_token=os.getenv("GITHUB_TOKEN"),
            github_username=os.getenv("GITHUB_USERNAME"),
        )
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

        # Configure Git user info
        # setup_git_user_config(self.context["repo_path"])

        # Get current files for context

    def cleanup(self):
        """Cleanup workspace."""
        # Make sure we're not in the repo directory before cleaning up
        if os.getcwd() == self.context.get("repo_path", ""):
            os.chdir(self.original_dir)

        # Clean up the repository directory
        cleanup_repository(self.original_dir, self.context.get("repo_path", ""))
        # Clean up the MongoDB

    def run(self):
        self.setup()

        # Create a feature branch
        log_section("CREATING FEATURE BRANCH")
        branch_phase = phases.BranchCreationPhase(workflow=self)
        branch_result = branch_phase.execute()

        if not branch_result or not branch_result.get("success"):
            log_error(Exception("Branch creation failed"), "Branch creation failed")
            return {
                "success": False,
                "message": "Branch creation failed",
                "data": None,
            }

        # Store branch name in context
        self.context["head"] = branch_result["data"]["branch_name"]
        log_key_value("Branch created", self.context["head"])

        # Classify repository
        repo_classification_result = self.classify_repository()
        if not repo_classification_result or not repo_classification_result.get(
            "success"
        ):
            log_error(
                Exception("Repository classification failed"),
                "Repository classification failed",
            )
            return {
                "success": False,
                "message": "Repository classification failed",
                "data": None,
            }

        # Get prompt name for README generation
        prompt_name = repo_classification_result["data"].get("repo_type")
        if not prompt_name:
            log_error(
                Exception("No prompt name returned from repository classification"),
                "Repository classification failed to provide prompt name",
            )
            return {
                "success": False,
                "message": "Repository classification failed to provide prompt name",
                "data": None,
            }

        # Generate README file
        for i in range(3):
            if i > 0:
                prompt_name = "other"
            readme_result = self.generate_readme_file(prompt_name)
            if not readme_result or not readme_result.get("success"):
                log_error(
                    Exception("README generation failed"), "README generation failed"
                )
                return {
                    "success": False,
                    "message": "README generation failed",
                    "data": None,
                }
            if readme_result.get("success"):
                review_result = self.review_readme_file(readme_result)
                if not review_result or not review_result.get("success"):
                    log_error(Exception("README review failed"), "README review failed")
                    return {
                        "success": False,
                        "message": "README review failed",
                        "data": None,
                    }
                log_key_value("README review result", review_result.get("data"))
                if (
                    review_result.get("success")
                    and review_result.get("data").get("recommendation") == "APPROVE"
                ):
                    result = self.create_pull_request()
                    return result
                else:
                    self.context["previous_review_comments_section"] = PROMPTS[
                        "previous_review_comments"
                    ] + review_result.get("data").get("comment")

        return {
            "success": False,
            "message": "README Review Exceed Max Attempts",
            "data": None,
        }

    def classify_repository(self):
        try:
            log_section("CLASSIFYING REPOSITORY TYPE")
            repo_classification_phase = phases.RepoClassificationPhase(workflow=self)
            return repo_classification_phase.execute()
        except Exception as e:
            log_error(e, "Repository classification workflow failed")
            return {
                "success": False,
                "message": f"Repository classification workflow failed: {str(e)}",
                "data": None,
            }

    def review_readme_file(self, readme_result):
        """Execute the issue generation workflow."""
        try:
            log_section("REVIEWING README FILE")
            review_readme_file_phase = phases.ReadmeReviewPhase(workflow=self)
            return review_readme_file_phase.execute()
        except Exception as e:
            log_error(e, "Readme file review workflow failed")
            return {
                "success": False,
                "message": f"Readme file review workflow failed: {str(e)}",
                "data": None,
            }

    def generate_readme_section(self, section):
        """Create the subsections of the README file."""

        self.context["section_name"] = section["name"]
        self.context["section_description"] = section["description"]

        try:

            # ==================== Generate README file ====================
            log_section("GENERATING README SECTION")
            generate_readme_section_phase = phases.ReadmeSectionGenerationPhase(
                workflow=self
            )
            readme_result = generate_readme_section_phase.execute()

            # Check README Generation Result
            if not readme_result or not readme_result.get("success"):
                log_error(
                    Exception(readme_result.get("error", "No result")),
                    "Readme file generation failed",
                )
                return None

            return readme_result

        except Exception as e:
            log_error(e, "Readme file generation workflow failed")
            return {
                "success": False,
                "message": f"Readme file generation workflow failed: {str(e)}",
                "data": None,
            }

    def generate_readme_file(self, repo_type):
        """Generate the README file."""

        readme_sections_spec = (
            list(INITIAL_SECTIONS)
            + list(DOCS_SECTIONS[repo_type])
            + list(FINAL_SECTIONS)
        )

        self.context["repo_type"] = repo_type
        self.context["all_sections"] = ", ".join(
            [section["name"] for section in readme_sections_spec]
        )
        try:
            readme_sections = []
            for section in readme_sections_spec:
                readme_result = self.generate_readme_section(section)
                print("README RESULT", readme_result)
                if not readme_result or not readme_result.get("success"):
                    log_error(
                        Exception(readme_result.get("error", "No result")),
                        "Readme file generation failed",
                    )
                    return None

                readme_section_content = readme_result.get("data", {}).get(
                    "section_content"
                )
                if readme_section_content:
                    readme_section_title = readme_result.get("data", {}).get(
                        "section_name"
                    )

                    readme_section = (
                        f"## {readme_section_title}\n\n" f"{readme_section_content}"
                    )
                    readme_sections.append(readme_section)

            self.context["readme_content"] = "\n\n".join(readme_sections)

            generate_readme_file_phase = phases.ReadmeFileCreationPhase(workflow=self)
            return generate_readme_file_phase.execute()

        except Exception as e:
            log_error(e, "Readme file generation workflow failed")
            return {
                "success": False,
                "message": f"Readme file generation workflow failed: {str(e)}",
                "data": None,
            }

    def create_pull_request(self):
        """Create a pull request for the README file."""
        try:
            log_section("CREATING PULL REQUEST")

            # Add required PR title and description parameters to context
            self.context["title"] = (
                f"Prometheus: Add README for {self.context['repo_name']}"
            )
            self.context["description"] = (
                f"This PR adds a README file for the {self.context['repo_name']} repository."
            )

            log_key_value(
                "Creating PR",
                f"from {self.context['head']} to {self.context['base']}",
            )

            print("CONTEXT", self.context)
            create_pull_request_phase = phases.CreatePullRequestPhase(workflow=self)
            return create_pull_request_phase.execute()
        except Exception as e:
            log_error(e, "Pull request creation workflow failed")
            return {
                "success": False,
                "message": f"Pull request creation workflow failed: {str(e)}",
                "data": None,
            }
