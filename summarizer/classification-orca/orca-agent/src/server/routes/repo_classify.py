from flask import Blueprint, jsonify, request
from src.server.services import repo_classification_service

bp = Blueprint("repo_classify", __name__)


@bp.post("/repo_classify")
def start_task():
    logger = repo_classification_service.logger
    logger.info(f"Task started")

    data = request.get_json()
    logger.info(f"Task data: {data}")
    
    if not data.get("repo_url"):
        return jsonify({"error": "Missing repo_url"}), 401

    result = repo_classification_service.handle_task_creation(
        repo_url=data["repo_url"],
    )

    return result

if __name__ == "__main__":
    from flask import Flask
    
    # Create a Flask app instance
    app = Flask(__name__)
    app.register_blueprint(bp)
    
    # Test data
    test_data = {
        "repo_url": "https://github.com/koii-network/docs"
    }
    
    # Set up test context
    with app.test_client() as client:
        # Make a POST request to the endpoint
        response = client.post(
            "/repo_classify/1",
            json=test_data
        )
        
        # Print the response
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.get_json()}")
