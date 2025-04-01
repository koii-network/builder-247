"""Prompts for the task decomposition workflow."""

PROMPTS = {
    "system_prompt": (
        "You are an expert software architect and technical lead specializing in breaking down complex "
        "features into small, manageable tasks. You excel at creating detailed, actionable subtasks "
        "with clear acceptance criteria. You understand software development best practices and "
        "focus on creating tasks that follow the Single Responsibility Principle."
    ),
    "generate_issues": (
        "Your task is to create a list of issues from a feature breakdown.\n"
        "The issue should be a small, discrete task that can be implemented in a single PR.\n"
        "Feature: {issue_spec}\n"
        "Repository: {repo_url}\n"
        "For each issue, you must provide:\n"
        "1. A clear, specific title\n"
        "2. A detailed description of the issue\n"
    ),
    "decompose_feature": (
        "Your task is to break down the following feature request into small, discrete subtasks:\n\n"
        "Feature: {feature_spec}\n"
        "Repository: {repo_url}\n"
        "For each subtask, you must provide:\n"
        "1. A clear, specific title\n"
        "2. A detailed description of the work required\n"
        "3. Quantifiable acceptance criteria that can be verified through automated tests\n\n"
        "Guidelines for task breakdown:\n"
        "- Each task should follow the Single Responsibility Principle - do one thing and do it well\n"
        "- Tasks should represent a single logical change (e.g., one schema change, one API endpoint)\n"
        "- Tasks should be independently testable with specific test cases\n"
        "- Each acceptance criterion must be measurable through unit tests, integration tests, or E2E tests\n"
        "- Include specific test coverage requirements (e.g., '100% branch coverage for error handling')\n"
        "- Tasks should be small enough that their implementation approach is clear\n"
        "- Consider separation of concerns (e.g., separate backend/frontend/database tasks)\n"
        "- Include necessary setup/infrastructure tasks\n"
        "- Tasks should be specific and focused\n"
        "- Tasks should include detailed steps\n"
        "- Consider using try logic to handle potential exceptions appropriately\n\n"
        "Current repository structure:\n{current_files}\n\n"
        "Format each subtask as follows:\n"
        "---\n"
        "Title: [Concise task title]\n"
        "Description: [Detailed explanation]\n"
        "Acceptance Criteria:\n"
        "- Test: [Specific test description with expected input/output]\n"
        "- Coverage: [Required test coverage percentage or specific paths to cover]\n"
        "- Performance: [Measurable performance criteria if applicable]\n"
        "---\n"
    ),
    "validate_subtasks": (
        "Review the following subtasks to ensure they meet these criteria:\n"
        "1. Each task follows the Single Responsibility Principle\n"
        "2. Each task represents a single logical change\n"
        "3. Each acceptance criterion is quantifiably measurable through automated tests\n"
        "4. Test coverage requirements are explicitly specified\n"
        "5. Performance criteria are measurable where applicable\n"
        "6. No critical aspects of the feature are missing\n\n"
        "Subtasks to validate:\n{subtasks}\n\n"
        "If any issues are found, provide specific recommendations for improvement."
    ),
    "regenerate_subtasks": (
        "Your task is to regenerate the following small, discrete subtasks based on the feedback provided:\n\n"
        "Failed Subtasks: {auditedSubtasks}\n"
        "Feedbacks: {feedbacks}\n"
        "For each subtask, you must provide:\n"
        "1. A clear, specific title\n"
        "2. A detailed description of the work required\n"
        "3. Quantifiable acceptance criteria that can be verified through automated tests\n\n"
        "Guidelines for task breakdown:\n"
        "- Each task should follow the Single Responsibility Principle - do one thing and do it well\n"
        "- Tasks should represent a single logical change (e.g., one schema change, one API endpoint)\n"
        "- Tasks should be independently testable with specific test cases\n"
        "- Each acceptance criterion must be measurable through unit tests, integration tests, or E2E tests\n"
        "- Include specific test coverage requirements (e.g., 'Full branch coverage for error handling')\n"
        "- Tasks should be small enough that their implementation approach is clear\n"
        "- Consider separation of concerns (e.g., separate backend/frontend/database tasks)\n"
        "- Include necessary setup/infrastructure tasks\n"
        "- Tasks should be specific and focused\n"
        "- Tasks should include detailed steps\n"
        "- Consider using try logic to handle potential exceptions appropriately\n\n"
        "Current repository structure:\n{current_files}\n\n"
        "Format each subtask as follows:\n"
        "---\n"
        "Title: [Concise task title]\n"
        "Description: [Detailed explanation]\n"
        "Acceptance Criteria:\n"
        "- Test: [Specific test description with expected input/output]\n"
        "- Coverage: [Required test coverage percentage or specific paths to cover]\n"
        "- Performance: [Measurable performance criteria if applicable]\n"
        "---\n"
    ),
    "dependency_tasks": (
        "Review the following given target task and determine if it depends on any other tasks.\n"
        "TargetTask: {target_task}\n"
        "Subtasks:\n{subtasks}\n\n"
        "If any dependencies are found, link the subtasks together.\n"
        "Format the output as follows:\n"
        "---\n"
        "Task UUID: [UUID of the target task]\n"
        "Dependency Tasks: [List of UUIDs of dependency tasks choose from subtasks]\n"
        "---\n"
    ),

}
