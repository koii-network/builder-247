from typing import Dict, List, Any
from prometheus_swarm.utils.logging import log_key_value, log_error
from prometheus_swarm.types import ToolOutput   

import uuid



def generate_tasks(
    tasks: List[Dict[str, Any]] = None,
    **kwargs,
) -> dict:
    """Generate a Task List for the repository.

    Args:
        tasks: List of task dictionaries, each containing:
            - title: Task title
            - description: Task description
            - acceptance_criteria: List of acceptance criteria

    Returns:
        dict: Result of the operation containing:
            - success: Whether the operation succeeded
            - message: Success/error message
            - data: Dictionary containing:
                - task_count: Number of tasks written
                - tasks: List of task dictionaries
            - error: Error message if any
    """
    try:
        for task in tasks:
            task_uuid = str(uuid.uuid4())
            task["uuid"] = task_uuid
        return {
            "success": True,
            "message": f"Successfully generated {len(tasks)} tasks",
            "data": {
                "task_count": len(tasks),
                "tasks": tasks,
            },
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to generate tasks: {str(e)}",
            "data": None,
            "error": str(e),
        }    

def regenerate_tasks(
    tasks: List[Dict[str, Any]] = None,
    **kwargs,
) -> dict:
    """Regenerate the tasks.

    Args:
        tasks: List of task dictionaries, each containing:
            - title: Task title
            - description: Task description
            - acceptance_criteria: List of acceptance criteria
            - uuid: UUID of the task

    Returns:
        dict: Result of the operation containing:
            - success: Whether the operation succeeded
            - message: Success/error message
            - data: Dictionary containing:
                - task_count: Number of tasks written
                - tasks: List of task dictionaries
            - error: Error message if any
    """
    try:
        return {
            "success": True,
            "message": f"Successfully regenerated {len(tasks)} tasks",
            "data": {
                "task_count": len(tasks),
                "tasks": tasks,
            },
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to regenerate tasks: {str(e)}",
            "data": None,
            "error": str(e),
        }   
    
def validate_tasks(decisions: List[Dict[str, Any]], **kwargs) -> dict:
    """Validate the tasks.

    Args:
        decisions: List of decisions, each containing:
            - uuid: UUID of the task
            - comment: Comment on the task
            - decision: Decision on the task, True or False

    Returns:
        dict: Result of the operation containing:
            - success: Whether the operation succeeded
            - message: Success/error message
            - data: Dictionary containing:
                - decision_count: Number of decisions
                - decisions: Dictionary of decision dictionaries
            - error: Error message if any
    """
    try:
        decisions_dict = {}
        for decision in decisions:
            if decision["decision"] == True:
                decisions_dict[decision["uuid"]] = decision
        return {
            "success": True,
            "message": f"Successfully validated {len(decisions)} tasks",
            "data": {
                "decision_count": len(decisions_dict),
                "decisions": decisions_dict,
            },
            "error": None,
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to validate tasks: {str(e)}",
            "data": None,
            "error": str(e),
        }


def create_task_dependency(task_uuid: str, dependency_tasks: List[str], **kwargs) -> dict:
    """Create the task dependency for a task.

    Args:
        task_uuid: UUID of the task
        dependency_tasks: List of UUIDs of dependency tasks

    Returns:
        dict: Result of the operation containing:
            - success: Whether the operation succeeded
            - message: Success/error message
            - data: Dictionary containing:
                - task_uuid: UUID of the task
                - dependency_tasks: List of UUIDs of dependency tasks
    """
    try:
        # Create a new dict one is task_uuid and value is dependency_tasks
        dependency_tasks_dict = {task_uuid: dependency_tasks}
        return {
            "success": True,
            "message": f"Successfully updated dependency tasks for {task_uuid}",
            "data": dependency_tasks_dict,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "message": f"Failed to update dependency tasks: {str(e)}", "data": None}
    
def generate_issues(
    issues: List[Dict[str, Any]] = None,
     **kwargs,
) -> dict:
    """Generate issues for the repository.

    Args:
        issues: List of issue dictionaries, each containing:
            - title: Issue title
            - description: Issue description
            - acceptance_criteria: List of acceptance criteria

    Returns:
        dict: Result of the operation containing:
            - success: Whether the operation succeeded
            - message: Success/error message
            - data: Dictionary containing:
                - issue_count: Number of issues generated
                - issues: List of issue dictionaries with UUIDs
            - error: Error message if any
    """
    try:
        for issue in issues:
            issue_uuid = str(uuid.uuid4())
            issue["uuid"] = issue_uuid
        return {
            "success": True,
            "message": f"Successfully generated {len(issues)} issues",
            "data": {
                "issue_count": len(issues),
                "issues": issues,
            },
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to generate issues: {str(e)}",
            "data": None,
            "error": str(e),
        }   
def audit_tasks(
    result: bool,
     **kwargs,
) -> dict:
    """Audit the tasks.
    """
    try:
        return {
            "success": True,
            "message": f"Successfully audited tasks",
            "data": {
                "result": result,
            },
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to validate tasks: {str(e)}",
            "data": None,
            "error": str(e),
        }