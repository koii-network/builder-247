PROMPTS = {
    "setup_repository": (
        "You are working on implementing the following task:\n"
        "{todo}\n\n"
        "First, create a descriptive branch name for this task. The branch name should:\n"
        "1. Be kebab-case (lowercase with hyphens)\n"
        "2. Be descriptive of the task\n"
        "3. Be concise (max 50 chars)\n"
        "4. Not include special characters\n\n"
        "Use the create_branch tool to create this branch."
    ),
    "files": "Available files: {files}",
    "execute_todo": (
        "You are working on implementing the following task:\n"
        "{todo}\n\n"
        "Available files: {files_directory}\n\n"
        "Please implement the task following these guidelines:\n"
        "1. Write clear, well-documented code\n"
        "2. Include comprehensive tests\n"
        "3. Follow best practices for the language/framework\n"
        "4. Handle edge cases and errors appropriately\n"
        "5. Ensure all tests pass\n\n"
        "Use the available tools to:\n"
        "1. Create/edit necessary files\n"
        "2. Run tests to verify your implementation\n"
        "3. Fix any issues until all tests pass"
    ),
    "fix_implementation": (
        "The previous implementation attempt had the following issues:\n"
        "{previous_issues}\n\n"
        "You are working on fixing the implementation for:\n"
        "{todo}\n\n"
        "Available files: {files_directory}\n\n"
        "Please fix the implementation to address all issues:\n"
        "1. Review and understand the reported problems\n"
        "2. Make necessary changes to fix each issue\n"
        "3. Ensure changes don't introduce new problems\n"
        "4. Run tests to verify your fixes\n"
        "5. Confirm all acceptance criteria are met\n\n"
        "Use the available tools to:\n"
        "1. Read and analyze the current code\n"
        "2. Make necessary modifications\n"
        "3. Run tests to verify your changes\n"
        "4. Continue until all issues are resolved"
    ),
    "validate_criteria": (
        "Please validate that the implementation meets all acceptance criteria:\n"
        "Acceptance Criteria:\n"
        "{acceptance_criteria}\n\n"
        "Follow these steps:\n"
        "1. Run the tests and verify they all pass\n"
        "2. Check each acceptance criterion carefully\n"
        "3. Verify code quality and best practices\n"
        "4. Check error handling and edge cases\n\n"
        "Use the available tools to:\n"
        "1. Run tests (they MUST pass)\n"
        "2. Review the implementation\n"
        "3. Verify each criterion\n\n"
        "Provide a detailed response with:\n"
        "1. Test results\n"
        "2. Status of each criterion (met/not met)\n"
        "3. Any issues found\n"
        "4. Required fixes (if any)\n\n"
        "Return:\n"
        "- success: true if ALL criteria are met\n"
        "- error: detailed explanation if any criteria are not met"
    ),
    "create_pr": (
        "Create a pull request for the implemented task:\n"
        "Repository: {repo_full_name}\n"
        "Branch: {head}\n"
        "Base: {base}\n\n"
        "Task Description:\n"
        "{todo}\n\n"
        "Acceptance Criteria:\n"
        "{acceptance_criteria}\n\n"
        "The PR title should be clear and descriptive.\n"
        "The PR description should include:\n"
        "1. Summary of changes\n"
        "2. Implementation details\n"
        "3. Testing approach\n"
        "4. How acceptance criteria are met"
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
