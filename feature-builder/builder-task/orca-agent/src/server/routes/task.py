from flask import Blueprint, request, jsonify
from ..utils.replay_prevention import replay_prevention

task_routes = Blueprint('task_routes', __name__)

@task_routes.route('/tasks', methods=['POST'])
@replay_prevention(max_request_age=300)  # 5-minute request expiration
def create_task():
    """
    Create a new task with replay attack prevention.
    Requires X-Request-Nonce and X-Request-Timestamp headers.
    
    :return: JSON response with task details
    """
    task_data = request.json
    # Your existing task creation logic here
    return jsonify({
        "status": "success",
        "message": "Task created",
        "task_id": "example-task-id"
    }), 201