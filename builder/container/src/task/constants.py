PROMPTS = {
    "setup_repository": "You're working in an existing repository at {repo_path}. "
    "Please create a new branch off main and give it a name that describes the task: {todo}",
    "files": "Below is the list of files in the repository: {files}.",
    "commit": "Please make a commit with a descriptive message. "
    "Give the commit a message that describes the task: {todo}",
    "push": "Please push the changes to the remote repository.",
    "create_pr": (
        "Create pull request from {head} to {base} in {repo_full_name}. "
        "Title: {todo}. Body: {acceptance_criteria}"
    ),
}
