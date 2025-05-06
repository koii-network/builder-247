from typing import Dict, Any
from feature_builder.builder_task.orca_agent.src.server.utils.replay_prevention import replay_preventer

def task_submission(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle task submission with replay attack prevention.
    
    Args:
        request_data (Dict[str, Any]): Task submission request data.
    
    Returns:
        Dict[str, Any]: Submission result or error response.
    """
    # Check for replay attack first
    if replay_preventer.is_replay_attack(request_data):
        return {
            "status": "error",
            "message": "Potential replay attack detected. Request rejected."
        }
    
    # Proceed with normal task submission logic
    try:
        # Your existing task submission implementation
        return {
            "status": "success",
            "message": "Task submitted successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }