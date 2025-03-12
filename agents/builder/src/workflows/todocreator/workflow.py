"""Task decomposition workflow implementation."""

import os
from github import Github
from src.workflows.base import Workflow
from src.tools.github_operations.implementations import fork_repository
from src.utils.logging import log_section, log_key_value, log_error
from src.workflows.todocreator import phases
from src.workflows.utils import (
    check_required_env_vars,
    validate_github_auth,
    setup_repo_directory,
    setup_git_user_config,
    cleanup_repo_directory,
    get_current_files,
)
from src.workflows.todocreator.utils import TaskModel, insert_task_to_mongodb

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


class TodoCreatorWorkflow(Workflow):
    def __init__(
        self,
        client,
        prompts,
        repo_url,
        feature_spec,
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
        self.feature_spec = feature_spec

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

        # Get current files for context
        self.context["current_files"] = get_current_files()

        # Add feature spec to context
        self.context["feature_spec"] = self.feature_spec
        

    def cleanup(self):
        """Cleanup workspace."""
        # Make sure we're not in the repo directory before cleaning up
        if os.getcwd() == self.context.get("repo_path", ""):
            os.chdir(self.original_dir)

        # Clean up the repository directory
        cleanup_repo_directory(self.original_dir, self.context.get("repo_path", ""))
        # Clean up the MongoDB

    def run(self):
        """Execute the task decomposition workflow."""
        try:
            self.setup()

            # Store the output filename in the context for the agent to use
            # Make sure it has a .csv extension


            # Decompose feature into tasks and generate CSV
            decompose_phase = phases.TaskDecompositionPhase(workflow=self)
            decomposition_result = decompose_phase.execute()

            if not decomposition_result or not decomposition_result.get("success"):
                log_error(
                    Exception(decomposition_result.get("error", "No result")),
                    "Task decomposition failed",
                )
                return None

            # Get the tasks and file path from the result
            tasks_data = decomposition_result["data"].get("tasks", [])
            output_json = decomposition_result["data"].get("file_path")
            task_count = decomposition_result["data"].get("task_count", 0)

            if not tasks_data:
                log_error(
                    Exception("No tasks generated"),
                    "Task decomposition failed",
                )
                return None

            # Convert raw tasks to Task objects
   
            
            log_key_value("JSON file created at", output_json)
            log_key_value("Tasks created", task_count)
            self.context["subtasks"] = tasks_data
            print(self.context["subtasks"])
            # Validation phase
            validation_phase = phases.TaskValidationPhase(workflow=self)
            validation_result = validation_phase.execute()

            if not validation_result or not validation_result.get("success"):
                log_error(
                    Exception(validation_result.get("error", "No result")),
                    "Task validation failed",
                )
            decisions = validation_result["data"]["decisions"]
            
            # TODO: Rework until all the tasks are valid
            self.context["auditedSubtasks"] = []
            # decisions_flag =  True
            for uuid, decision in decisions.items():
                # decision["decision"] = False
                if decision["decision"] == False:
                    task = next((task for task in tasks_data if task["uuid"] == uuid), None)
                    if task:
                        self.context["auditedSubtasks"].append(task)
                    # decisions_flag = False
            
            self.context["feedbacks"] = decisions
            if len(self.context["auditedSubtasks"]) > 0:
                regenerate_phase = phases.TaskRegenerationPhase(workflow=self)
                regenerate_result = regenerate_phase.execute()
                if not regenerate_result or not regenerate_result.get("success"):
                    log_error(
                        Exception(regenerate_result.get("error", "No result")),
                        "Task regeneration failed",
                    )
                # replace the tasks with the new tasks
                regenerated_tasks_data = regenerate_result["data"]["tasks"]
                # replace the self.context["subtasks"] with the new tasks
                for task in regenerated_tasks_data:
       
                    index = next((i for i, t in enumerate(tasks_data) if t["uuid"] == task["uuid"]), None)
                    if index is not None:
                        # decisions[task["uuid"]]["decision"] = True
                        tasks_data[index] = task
                    else:
            
                        tasks_data.append(task)

            # Print regenerated tasks
            print("Regenerated tasks:")
            print(tasks_data)

            # Ensure the code continues to execute after printing
            # # TODO: Dependency Phase
            for task in tasks_data:
                self.context["target_task"] = task
                dependency_phase = phases.TaskDependencyPhase(workflow=self)
                dependency_result = dependency_phase.execute()
                if not dependency_result or not dependency_result.get("success"):
                    log_error(
                        Exception(dependency_result.get("error", "No result")),
                        "Task dependency failed",
                    )
                print(dependency_result["data"])
                print(task["uuid"])
                task["dependency_tasks"] = dependency_result["data"][task["uuid"]]

            
            # Insert into MongoDB
            for task in tasks_data:
                if decisions[task["uuid"]]["decision"] == True:
                    print(task["title"])
                    task_model = TaskModel(
                        title=task["title"],
                        description=task["description"],
                        acceptance_criteria=task["acceptance_criteria"],
                        repoOwner=self.context["repo_owner"],
                        repoName=self.context["repo_name"],
                        dependencyTasks=task["dependency_tasks"]
                    )
                    insert_task_to_mongodb(task_model)

            # Return the final result
            return {
                "success": True,
                "message": f"Created {task_count} tasks for the feature",
                "data": {
                    "decisions": tasks_data,
                    "task_count": task_count,
                },
            }

        except Exception as e:
            log_error(e, "Task decomposition workflow failed")
            return {
                "success": False,
                "message": f"Task decomposition workflow failed: {str(e)}",
                "data": None,
            }
        finally:
            self.cleanup()
