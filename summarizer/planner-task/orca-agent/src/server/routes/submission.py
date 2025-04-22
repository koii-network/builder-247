# from flask import Blueprint, jsonify
# from prometheus_swarm.database import get_db, Submission
# import logging

# logger = logging.getLogger(__name__)

# bp = Blueprint("submission", __name__)


# @bp.get("/submission/<roundNumber>")
# def fetch_submission(roundNumber):
#     logger.info(f"Fetching submission for round: {roundNumber}")

#     db = get_db()
#     submission = (
#         db.query(Submission)
#         .filter(
#             Submission.round_number == int(roundNumber),
#             Submission.status == "completed",
#         )
#         .first()
#     )

#     if submission:
#         return jsonify(
#             {
#                 "roundNumber": submission.round_number,
#                 "prUrl": submission.pr_url,
#                 "githubUsername": submission.username,
#                 "repoOwner": submission.repo_owner,
#                 "repoName": submission.repo_name,
#             }
#         )
#     else:
#         return jsonify({"error": "Submission not found"}), 404
