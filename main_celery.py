# not in use, for possible future use

# from flask import Flask, request, jsonify
# from src.task.flow import todo_to_pr
# from src.task.celery_app import celery

# app = Flask(__name__)


# @celery.task
# def run_todo_task(todo, acceptance_criteria):
#     try:
#         todo_to_pr(todo=todo, acceptance_criteria=acceptance_criteria)
#     except Exception as e:
#         print(f"Background task failed: {str(e)}")


# @app.route("/create-pr", methods=["POST"])
# def create_pr():
#     data = request.get_json()
#     todo = data.get("todo")
#     acceptance_criteria = data.get("acceptance_criteria", "")

#     # Start the task asynchronously
#     task = run_todo_task.delay(todo, acceptance_criteria)

#     return (
#         jsonify(
#             {
#                 "status": "accepted",
#                 "message": "PR creation process started",
#                 "task_id": task.id,  # Celery provides task tracking
#             }
#         ),
#         202,
#     )


# if __name__ == "__main__":
#     app.run(debug=True)
