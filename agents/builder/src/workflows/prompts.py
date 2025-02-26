PROMPTS = {
    "setup_repository": (
        "Create a descriptive branch name for the following task: {todo}. The branch name should:\n"
        "1. Be kebab-case (lowercase with hyphens)\n"
        "2. Be descriptive of the task\n"
        "3. Be concise (max 50 chars)\n"
        "4. Not include special characters"
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
        "Continuing in the same conversation, you are working on fixing the implementation for:\n"
        "{todo}\n\n"
        "Available files: {files_directory}\n\n"
        "IMPORTANT: Always use relative paths (e.g., 'src/file.py' not '/src/file.py')\n\n"
        "Use the available tools to:\n"
        "1. Review and understand the reported problems\n"
        "2. Make necessary changes to fix each issue\n"
        "3. Ensure changes don't introduce new problems\n"
        "4. Run tests to verify your fixes\n"
        "5. Confirm all acceptance criteria are met\n\n"
        "STOP after fixing the implementation, do not create a pull request."
    ),
    "validate_criteria": (
        "You are validating the implementation of the following task:\n"
        "{todo}\n\n"
        "Available files: {files_directory}\n\n"
        "Acceptance Criteria:\n"
        "{acceptance_criteria}\n\n"
        "IMPORTANT: Always use relative paths (e.g., 'src/file.py' not '/src/file.py')\n\n"
        "Steps to validate:\n"
        "1. First examine the available files to understand the implementation\n"
        "2. Run the tests and verify they all pass\n"
        "3. Check each acceptance criterion carefully\n"
        "4. Verify code quality and best practices\n"
        "5. Check error handling and edge cases\n"
        "6. Verify correct directory structure:\n"
        "   - Implementation code MUST be in 'src' directory\n"
        "   - Test files MUST be in 'tests' directory\n\n"
        "Provide a detailed validation report with:\n"
        "1. Test Results:\n"
        "   - List of passing tests\n"
        "   - List of failing tests\n"
        "2. Acceptance Criteria Status:\n"
        "   - List of criteria that are met\n"
        "   - List of criteria that are not met\n"
        "3. Directory Structure Check:\n"
        "   - Whether structure is valid\n"
        "   - Any structural issues found\n"
        "4. List of all issues found\n"
        "5. List of required fixes\n\n"
        "Use the validate_implementation tool to submit your findings.\n"
        "The tool requires:\n"
        "- success: boolean indicating if ALL criteria are met\n"
        "- test_results: object with passed and failed test lists\n"
        "- criteria_status: object with met and not_met criteria lists\n"
        "- directory_check: object with valid boolean and issues list\n"
        "- issues: list of all issues found\n"
        "- required_fixes: list of fixes needed\n\n"
        "STOP after submitting the validation report."
    ),
    "create_pr": (
        "You are creating a pull request for the following task:\n"
        "Repository: {repo_full_name}\n"
        "Branch: {head}\n"
        "Base: {base}\n\n"
        "Task Description:\n"
        "{todo}\n\n"
        "Available files: {files_directory}\n\n"
        "Acceptance Criteria:\n"
        "{acceptance_criteria}\n\n"
        "IMPORTANT: Always use relative paths (e.g., 'src/file.py' not '/src/file.py')\n\n"
        "Steps to create the pull request:\n"
        "1. First examine the available files to understand the implementation\n"
        "2. Create a clear and descriptive PR title\n"
        "3. Write a comprehensive PR description that includes:\n"
        "   - Description of all changes made\n"
        "   - Implementation details for each component\n"
        "   - Testing approach and results\n"
        "   - How each acceptance criterion is met\n"
        "   - Any important notes or considerations"
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
{description}

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
{description}

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
REVIEW_SYSTEM_PROMPT = """You are a thorough code reviewer with expertise in Python, testing, and software
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

Be thorough but fair in your assessment. Approve PRs that meet all requirements, suggest revisions for minor issues,
and reject those with major problems."""
