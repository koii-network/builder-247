PROMPTS = {
    "setup_repository": (
        "Create a branch name for this task: {todo}\n"
        "Provide only the base name (without timestamp)\n"
        "Example format: 'feature/add-logging'"
    ),
    "files": "Below is the list of files in the repository: {files}.",
    "create_pr": (
        "Create pull request from {head} to {base} in {repo_full_name}.\n"
        "Todo: {todo}\n"
        "Acceptance Criteria: {acceptance_criteria}\n"
        "Title: A short title describing the task\n"
        "Provide these components:\n"
        "1. Summary of changes made\n"
        "2. List of tests with descriptions"
    ),
    "execute_todo": (
        "Execute the task: {todo}\n"
        "Files in the repository: {files_directory}\n"
        "All operations should be performed with relative paths."
        "After completing your changes, make sure to commit and push them to the remote branch."
    ),
}

PR_TEMPLATE = """# {title}

## Original Task
{todo}

## Summary of Changes
{summary}

## Acceptance Criteria
{acceptance_criteria}

## Tests
{tests}
"""

REVIEW_TEMPLATE = """# PR Review: {title}

## Recommendation: {recommendation}

### Justification
{recommendation_reasons}

## Summary of Changes
{summary}

## Requirements Review
### ✅ Met Requirements
{met_requirements}

### ❌ Unmet Requirements
{unmet_requirements}

## Test Evaluation
### Coverage
{test_coverage}

### Issues in Existing Tests
{test_issues}

### Missing Test Cases
{missing_tests}

## Action Items
{action_items}
"""
