from flask import Flask, request, jsonify, g
from src.task.flow import todo_to_pr
from threading import Thread
import sqlite3

app = Flask(__name__)

DATABASE = "database.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        cursor = g.db.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                roundNumber INTEGER PRIMARY KEY,
                submission TEXT,
                status TEXT DEFAULT 'pending'
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                model TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
            """
        )
        g.db.commit()
    return g.db


def close_db():
    db = g.pop("db", None)
    if db is not None:
        db.close()


def run_todo_task(round_number, todo, acceptance_criteria):
    try:
        # Connect to DB in the background thread
        db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row

        # Update status to "running"
        cursor = db.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO submissions (roundNumber, submission, status) VALUES (?, ?, ?)",
            (round_number, None, "running"),
        )
        db.commit()

        # Run the actual task
        result = todo_to_pr(todo=todo, acceptance_criteria=acceptance_criteria)

        # Store the result
        cursor.execute(
            "UPDATE submissions SET submission = ?, status = ? WHERE roundNumber = ?",
            (result, "completed", round_number),
        )
        db.commit()
    except Exception as e:
        print(f"Background task failed: {str(e)}")
        cursor.execute(
            "UPDATE submissions SET status = ? WHERE roundNumber = ?",
            ("failed", round_number),
        )
        db.commit()
    finally:
        db.close()


@app.get("/")
def home():
    return "Working"


@app.post("/healthz")
def health_check():
    return "OK"


@app.post("/task/<roundNumber>")
def start_task(roundNumber):
    print(f"Task started for round: {roundNumber}")
    data = request.get_json()
    todo = data.get("todo")
    acceptance_criteria = data.get("acceptance_criteria", "")

    # Start the task in background
    thread = Thread(
        target=run_todo_task, args=(int(roundNumber), todo, acceptance_criteria)
    )
    thread.daemon = True
    thread.start()

    return jsonify({"roundNumber": roundNumber, "status": "Task started"})


@app.get("/submission/<roundNumber>")
def fetch_submission(roundNumber):
    print(f"Fetching submission for round: {roundNumber}")
    db = get_db()
    cursor = db.cursor()
    query = cursor.execute(
        "SELECT * FROM submissions WHERE roundNumber = ?", (int(roundNumber),)
    )
    result = query.fetchone()
    close_db()

    if result:
        return jsonify({"submission": result["submission"], "status": result["status"]})
    else:
        return "Submission not found", 404


@app.post("/audit")
def audit_submission():
    print("Auditing submission")
    data = request.get_json()
    audit_result = data["submission"] == "Hello World!"
    return jsonify(audit_result)


if __name__ == "__main__":
    app.run(debug=True)
