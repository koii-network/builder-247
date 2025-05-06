from flask import Blueprint, request, jsonify
from ..middleware.replay_prevention import prevent_replay, ReplayPreventionError

task_routes = Blueprint('task_routes', __name__)

@task_routes.route('/submit_task', methods=['POST'])
@prevent_replay
def submit_task():
    """
    Submit a task with replay attack prevention.
    
    This route uses the replay prevention middleware to prevent 
    the same task from being submitted multiple times within a 
    short time window.
    
    :return: JSON response with task submission status
    :raises ReplayPreventionError: If a potential replay attack is detected
    """
    try:
        task_data = request.get_json()
        
        # Simulate task processing 
        # In a real-world scenario, add your actual task submission logic here
        return jsonify({
            "status": "success", 
            "message": "Task submitted successfully",
            "task_id": "example_task_id"
        }), 200
    
    except ReplayPreventionError:
        # Handle replay attack attempt
        return jsonify({
            "status": "error", 
            "message": "Potential replay attack detected"
        }), 400
    
    except Exception as e:
        # Handle other potential errors
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500