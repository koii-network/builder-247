PROMPTS = {
    "setup_repository": (
        "Create a branch name for this task: {todo}\n"
        "Provide only the base name (without timestamp)\n"
        "Example format: 'feature/add-logging'"
    ),
    "files": "Below is the list of files in the repository: {files}.",
    "commit": "If you have not already committed, please make a commit with a descriptive message. "
    "Give the commit a message that describes the task: {todo}",
    "push": "Please push the changes to the remote repository.",
    "create_pr": (
        "Create pull request from {head} to {base} in {repo_full_name}.\n"
        "Todo: {todo}\n"
        "Acceptance Criteria: {acceptance_criteria}\n"
        "Title: A short title describing the task\n"
        "Provide these components:\n"
        "1. Summary of changes made\n"
        "2. List of tests with descriptions"
    ),
}

PR_TEMPLATE = """# {title}

## Task
{todo}

## Acceptance Criteria
{acceptance_criteria}

## Summary of Changes
{summary}

## List of Tests
{tests}"""
