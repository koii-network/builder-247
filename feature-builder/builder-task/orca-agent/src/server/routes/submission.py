from flask import Blueprint, request, jsonify
from ..utils.replay_prevention import replay_prevention

submission_routes = Blueprint('submission_routes', __name__)

@submission_routes.route('/submissions', methods=['POST'])
@replay_prevention(max_request_age=300)  # 5-minute request expiration
def create_submission():
    """
    Create a new submission with replay attack prevention.
    Requires X-Request-Nonce and X-Request-Timestamp headers.
    
    :return: JSON response with submission details
    """
    submission_data = request.json
    # Your existing submission creation logic here
    return jsonify({
        "status": "success", 
        "message": "Submission received",
        "submission_id": "example-submission-id"
    }), 201