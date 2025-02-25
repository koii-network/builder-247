PROMPTS = {
    "setup_repository": (
        "Create a descriptive branch name for the following task: {todo}. The branch name should:\n"
        "1. Be kebab-case (lowercase with hyphens)\n"
        "2. Be descriptive of the task\n"
        "3. Be concise (max 50 chars)\n"
        "4. Not include special characters\n"
        "STOP after creating the branch, do not being writing code."
    ),
    "execute_todo": (
        "You are working on implementing the following task:\n"
        "{todo}\n\n"
        "Available files: {files_directory}\n\n"
        "IMPORTANT: ALWAYS use relative paths (e.g., 'src/file.py' not '/src/file.py')\n\n"
        "Use the available tools to:\n"
        "Create/edit necessary files using relative paths\n"
        "Run tests to verify your implementation\n"
        "Fix any issues until all tests pass\n\n"
        "Please implement the task following these guidelines:\n"
        "1. Write clear, well-documented code\n"
        "2. Include comprehensive tests\n"
        "3. Follow best practices for the language/framework\n"
        "4. Handle edge cases and errors appropriately\n"
        "5. Ensure all tests pass\n"
        "STOP after implementing the task, do not create a pull request."
    ),
    "fix_implementation": (
        "The previous implementation attempt had the following issues:\n"
        "{previous_issues}\n\n"
        "You are working on fixing the implementation for:\n"
        "{todo}\n\n"
        "Available files: {files_directory}\n\n"
        "IMPORTANT: ALWAYS use relative paths (e.g., 'src/file.py' not '/src/file.py')\n\n"
        "Use the available tools to:\n"
        "Read and analyze the current code\n"
        "Make necessary modifications\n"
        "Run tests to verify your changes\n"
        "Continue until all issues are resolved\n\n"
        "Please fix the implementation to address all issues:\n"
        "1. Review and understand the reported problems\n"
        "2. Make necessary changes to fix each issue\n"
        "3. Ensure changes don't introduce new problems\n"
        "4. Run tests to verify your fixes\n"
        "5. Confirm all acceptance criteria are met\n"
        "STOP after fixing the implementation, do not create a pull request."
    ),
    "validate_criteria": (
        "Please validate that the implementation meets all acceptance criteria:\n"
        "Acceptance Criteria:\n"
        "{acceptance_criteria}\n\n"
        "Follow these steps:\n"
        "1. Run the tests and verify they all pass\n"
        "2. Check each acceptance criterion carefully\n"
        "3. Verify code quality and best practices\n"
        "4. Check error handling and edge cases\n"
        "5. Verify correct directory structure:\n"
        "   - Implementation code MUST be in 'src' directory\n"
        "   - Test files MUST be in 'tests' directory\n\n"
        "Provide a detailed response with:\n"
        "1. Test results\n"
        "2. Status of each criterion (met/not met)\n"
        "3. Directory structure check\n"
        "4. Any issues found\n"
        "5. Required fixes (if any)\n\n"
        "Return:\n"
        "- success: true if ALL criteria are met\n"
        "- error: detailed explanation if any criteria are not met"
        "STOP after validating the criteria, do not attempt to fix any issues or create a pull request."
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
        "4. How acceptance criteria are met\n"
        "STOP after creating the pull request, do not review your own pull request."
    ),
    "review_pr": (
        "Review pull request #{pr_number} in repository {repo}.\n\n"
        "The PR code has been checked out. The following files are available:\n"
        "{files_list}\n\n"
        "Requirements to check:\n"
        "{requirements}\n\n"
        "IMPORTANT: ALWAYS use relative paths (e.g., 'src/file.py' not '/src/file.py')\n\n"
        "Test requirements to verify (where applicable):\n"
        "1. Core Functionality Testing:\n"
        "   - Tests the actual implementation, not just mocks\n"
        "   - For external services (APIs, databases, etc.), includes both:\n"
        "     * Integration tests with real services\n"
        "     * Unit tests with mocks for edge cases\n"
        "   - Tests the complete workflow, not just individual parts\n"
        "2. Edge Cases and Input Validation:\n"
        "   - Tests boundary values and limits\n"
        "   - Tests invalid/malformed inputs\n"
        "   - Tests empty/null cases\n"
        "   - Tests type mismatches\n"
        "3. Error Handling:\n"
        "   - Tests error conditions (e.g., network failures, timeouts)\n"
        "   - Tests error recovery and cleanup\n"
        "4. Test Design:\n"
        "   - Tests are independent and deterministic\n"
        "   - No shared state between tests\n"
        "   - Mocks are used appropriately\n"
        "   - Tests all code paths and branches\n"
        "5. Performance and Resources:\n"
        "   - Tests with realistic data sizes\n"
        "   - Verifies performance requirements\n"
        "   - Tests resource cleanup\n\n"
        "Review criteria:\n"
        "- APPROVE if all requirements are met and tests pass\n"
        "- REVISE if there are minor issues: {minor_issues}\n"
        "- REJECT if there are major issues: {major_issues}\n\n"
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

# System prompts
REVIEW_SYSTEM_PROMPT = """You are a thorough code reviewer with expertise in Python, testing, and software \
engineering best practices. Your task is to review pull requests for coding challenges, focusing on:

1. Implementation correctness
2. Test coverage and quality
3. Code organization and structure
4. Error handling and edge cases
5. Performance considerations

For each review:
- Carefully examine all code changes
- Run and analyze tests
- Check implementation against requirements
- Look for potential issues or improvements
- Provide clear, actionable feedback

Be thorough but fair in your assessment. Approve PRs that meet all requirements, suggest revisions for minor issues, \
and reject those with major problems."""
