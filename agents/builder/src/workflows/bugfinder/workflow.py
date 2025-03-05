"""Bug finder workflow implementation."""

import os
from github import Github
from src.workflows.base import Workflow
from src.tools.github_operations.implementations import fork_repository
from src.utils.logging import log_section, log_key_value, log_error
from src.workflows.bugfinder import phases
from src.workflows.utils import (
    check_required_env_vars,
    validate_github_auth,
    setup_repo_directory,
    setup_git_user_config,
    cleanup_repo_directory,
    get_current_files,
)


class BugFinderWorkflow(Workflow):
    def __init__(
        self,
        client,
        prompts,
        repo_url,
        output_csv_path="bugs.csv",
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
            output_csv_path=output_csv_path,
        )
        self.bugs_found = []

    def setup(self):
        """Set up repository and workspace."""
        check_required_env_vars(["GITHUB_TOKEN", "GITHUB_USERNAME"])
        validate_github_auth(os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_USERNAME"))

        # Get the default branch from GitHub
        try:
            gh = Github(os.getenv("GITHUB_TOKEN"))
            repo = gh.get_repo(
                f"{self.context['repo_owner']}/{self.context['repo_name']}"
            )
            self.context["base_branch"] = repo.default_branch
            log_key_value("Default branch", self.context["base_branch"])
        except Exception as e:
            log_error(e, "Failed to get default branch, using 'main'")
            self.context["base_branch"] = "main"

        # Set up repository directory
        repo_path, original_dir = setup_repo_directory()
        self.context["repo_path"] = repo_path
        self.original_dir = original_dir

        # Fork and clone repository
        log_section("FORKING AND CLONING REPOSITORY")
        fork_result = fork_repository(
            f"{self.context['repo_owner']}/{self.context['repo_name']}",
            self.context["repo_path"],
        )
        if not fork_result["success"]:
            error = fork_result.get("error", "Unknown error")
            log_error(Exception(error), "Fork failed")
            raise Exception(error)

        # Enter repo directory
        os.chdir(self.context["repo_path"])

        # Configure Git user info
        setup_git_user_config(self.context["repo_path"])

        self.context["current_files"] = get_current_files()

    def cleanup(self):
        """Cleanup workspace."""
        # Make sure we're not in the repo directory before cleaning up
        if os.getcwd() == self.context.get("repo_path", ""):
            os.chdir(self.original_dir)

        # Clean up the repository directory
        cleanup_repo_directory(self.original_dir, self.context.get("repo_path", ""))

    def run(self):
        """Execute the bug finder workflow."""
        try:
            self.setup()

            # Store the output filename in the context for the agent to use
            # Make sure it has a .csv extension
            output_filename = self.context.get("output_csv_path", "bugs.csv")
            if not output_filename.endswith(".csv"):
                output_filename = f"{os.path.splitext(output_filename)[0]}.csv"
                self.context["output_csv_path"] = output_filename

            # Log the output filename that will be used
            log_key_value("Output CSV file", output_filename)

            # Analyze codebase
            analyze_phase = phases.CodeAnalysisPhase(workflow=self)
            analysis_result = analyze_phase.execute()

            if not analysis_result:
                log_error(
                    Exception("Analysis phase returned no result"), "Analysis failed"
                )
                return None

            # Log the analysis result structure for debugging
            log_key_value(
                "Analysis result keys",
                str(list(analysis_result.get("data", {}).keys())),
            )

            # The generate_analysis tool should have created the CSV file directly
            # Extract the file path and issue count from the result
            file_path = analysis_result["data"].get("file_path", "")
            issue_count = analysis_result["data"].get("issue_count", 0)

            # Verify the file exists at the path returned by the tool
            if file_path and os.path.exists(file_path):
                log_key_value("CSV file created at", file_path)
                log_key_value("Issues found", issue_count)

                # Store the file path in the context
                self.context["output_csv_path"] = file_path

                # For backward compatibility, also store the bugs
                self.bugs_found = []
                # If we have bugs in the result, store them
                if "bugs" in analysis_result["data"]:
                    self.bugs_found = analysis_result["data"]["bugs"]
            else:
                # If not found at the returned path, check if it's in the project's data directory
                project_data_dir = "/home/laura/git/github/builder-247/data"
                file_name = os.path.basename(
                    self.context.get("output_csv_path", "bugs.csv")
                )
                alternative_path = os.path.join(project_data_dir, file_name)

                if os.path.exists(alternative_path):
                    log_key_value("CSV file created at", alternative_path)
                    log_key_value("Issues found", issue_count)

                    # Store the file path in the context
                    self.context["output_csv_path"] = alternative_path

                    # For backward compatibility, also store the bugs
                    self.bugs_found = []
                    # If we have bugs in the result, store them
                    if "bugs" in analysis_result["data"]:
                        self.bugs_found = analysis_result["data"]["bugs"]
                else:
                    log_error(
                        Exception(
                            f"CSV file not found at {file_path} or {alternative_path}"
                        ),
                        "CSV file not created",
                    )
                    return {
                        "success": False,
                        "message": "Bug finder workflow failed: CSV file not created",
                        "data": None,
                    }

            return {
                "success": True,
                "message": f"Found {issue_count} issues in the repository",
                "data": {
                    "bugs": self.bugs_found,
                    "output_csv": self.context["output_csv_path"],
                    "issue_count": issue_count,
                },
            }
        except Exception as e:
            log_error(e, "Bug finder workflow failed")
            return {
                "success": False,
                "message": f"Bug finder workflow failed: {str(e)}",
                "data": None,
            }
        finally:
            self.cleanup()
