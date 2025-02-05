from flask import Flask, request, jsonify
from src.task.flow import todo_to_pr

app = Flask(__name__)

@app.route('/create-pr', methods=['POST'])
def create_pr():
    data = request.get_json()
    todo = data.get('todo')
    acceptance_criteria = data.get('acceptance_criteria', '')

    try:
        todo_to_pr(
            todo=todo,
            acceptance_criteria=acceptance_criteria
        )
        return jsonify({"status": "success", "message": "PR created successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
