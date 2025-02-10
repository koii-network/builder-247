from flask import Flask, request, jsonify, g
from src.task.flow import todo_to_pr
from threading import Thread
import sqlite3
from github import Github
import re
import os
import requests

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
                status TEXT DEFAULT 'pending',
                pr_url TEXT,
                username TEXT,
                repo_owner TEXT,
                repo_name TEXT
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


def run_todo_task(
    round_number,
    todo,
    acceptance_criteria,
    repo_owner,
    repo_name,
    signature,
    staking_key,
):
    with app.app_context():
        try:
            db = get_db()
            cursor = db.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO submissions
                (roundNumber, status, repo_owner, repo_name)
                VALUES (?, ?, ?, ?)
                """,
                (round_number, "running", repo_owner, repo_name),
            )
            db.commit()

            pr_url = todo_to_pr(
                todo=todo,
                acceptance_criteria=acceptance_criteria,
                repo_owner=repo_owner,
                repo_name=repo_name,
            )

            try:
                response = requests.post(
                    "https://builder247.koii.network/add-pr",
                    json={
                        "pr_url": pr_url,
                        "signature": signature,
                        "publicKey": staking_key,
                    },
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error submitting PR: {str(e)}")

            username = os.environ.get("GITHUB_USERNAME")

            cursor.execute(
                """
                UPDATE submissions
                SET status = ?, pr_url = ?, username = ?
                WHERE roundNumber = ?
                """,
                ("completed", pr_url, username, round_number),
            )
            db.commit()
        except Exception as e:
            print(f"Background task failed: {str(e)}")
            if "cursor" in locals():
                cursor.execute(
                    "UPDATE submissions SET status = ? WHERE roundNumber = ?",
                    ("failed", round_number),
                )
                db.commit()
        finally:
            close_db()


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
    repo_owner = data.get("repo_owner")
    repo_name = data.get("repo_name")
    signature = data.get("signature")
    staking_key = data.get("stakingKey")

    if not repo_owner or not repo_name:
        return jsonify({"error": "Missing repo_owner or repo_name"}), 400

    # Start the task in background
    thread = Thread(
        target=run_todo_task,
        args=(
            int(roundNumber),
            todo,
            acceptance_criteria,
            repo_owner,
            repo_name,
            signature,
            staking_key,
        ),
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
        """
        SELECT roundNumber, status, pr_url, username
        FROM submissions
        WHERE roundNumber = ? and status = 'completed'
        """,
        (int(roundNumber),),
    )
    result = query.fetchone()
    close_db()

    if result:
        return jsonify(
            {
                "roundNumber": result["roundNumber"],
                "status": result["status"],
                "pr_url": result["pr_url"],
                "username": result["username"],
            }
        )
    else:
        return "Submission not found", 404


@app.post("/audit")
def audit_submission():
    print("Auditing submission")
    data = request.get_json()
    round_number = data.get("roundNumber")
    signature = data.get("signature")
    staking_key = data.get("stakingKey")
    if not round_number:
        return jsonify({"error": "Missing roundNumber"}), 400

    db = get_db()
    cursor = db.cursor()
    query = cursor.execute(
        """
        SELECT pr_url, username, repo_owner, repo_name
        FROM submissions
        WHERE roundNumber = ? AND status = 'completed'
        """,
        (int(round_number),),
    )
    result = query.fetchone()
    close_db()

    if not result:
        return jsonify({"error": "Submission not found"}), 404

    is_valid = verify_pr_ownership(
        result["pr_url"],
        result["username"],
        result["repo_owner"],
        result["repo_name"],
        signature,
        staking_key,
    )
    return jsonify(is_valid)


def verify_pr_ownership(
    pr_url: str,
    expected_username: str,
    expected_owner: str,
    expected_repo: str,
    signature: str,
    staking_key: str,
) -> bool:
    """
    Verify that a PR was created by the expected user on the expected repository.
    """
    try:
        gh = Github(os.environ.get("GITHUB_TOKEN"))

        match = re.match(r"https://github.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
        if not match:
            print(f"Invalid PR URL format: {pr_url}")
            return False

        owner, repo_name, pr_number = match.groups()

        if owner != expected_owner or repo_name != expected_repo:
            print(
                f"Repository mismatch. Expected: {expected_owner}/{expected_repo}, Got: {owner}/{repo_name}"
            )
            return False

        repo = gh.get_repo(f"{owner}/{repo_name}")
        pr = repo.get_pull(int(pr_number))

        if pr.user.login != expected_username:
            print(
                f"Username mismatch. Expected: {expected_username}, Got: {pr.user.login}"
            )
            return False

        response = requests.post(
            "https://builder247.koii.network/check-todo",
            json={
                "pr_url": pr_url,
                "signature": signature,
                "publicKey": staking_key,
            },
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        result = response.json()
        if result["is_valid"]:
            return True
        else:
            print(f"PR is not valid: {result['reason']}")
            return False

    except Exception as e:
        print(f"Error verifying PR ownership: {str(e)}")
        return False


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
