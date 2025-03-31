"""Prompts for the task decomposition workflow."""

PROMPTS = {
    "system_prompt": (
        "You are an expert software architect and technical lead specializing in breaking down complex "
        "features into small, manageable tasks. You excel at creating detailed, actionable subtasks "
        "with clear acceptance criteria. You understand software development best practices and "
        "focus on creating tasks that follow the Single Responsibility Principle."
    ),
    "decompose_feature": (
        "Your task is to break down the following feature request into small, discrete subtasks:\n\n"
        "Feature: {feature_description}\n"
        "Repository: {repo_url}\n\n"
        "Output JSON: {output_json_path}\n\n"
        "For each subtask, you must provide:\n"
        "1. A clear, specific title\n"
        "2. A detailed description of the work required\n"
        "3. Clear acceptance criteria that can be verified\n\n"
        "Guidelines for task breakdown:\n"
        "- Each task should follow the Single Responsibility Principle - do one thing and do it well\n"
        "- Tasks should represent a single logical change (e.g., one schema change, one API endpoint)\n"
        "- Tasks should be independently testable\n"
        "- Tasks should be small enough that their implementation approach is clear\n"
        "- Consider separation of concerns (e.g., separate backend/frontend/database tasks)\n"
        "- Include necessary setup/infrastructure tasks\n"
        "- Consider testing requirements\n"
        "- Account for documentation needs\n"
        "- Work must be quantitative and measurable\n"
        "Current repository structure:\n{current_files}\n\n"
    ),
    "validate_subtasks": (
        "Review the following subtasks to ensure they meet these criteria:\n"
        "1. Each task follows the Single Responsibility Principle\n"
        "2. Each task represents a single logical change\n"
        "3. Tasks are independently testable\n"
        "4. Acceptance criteria are specific and verifiable\n"
        "5. No critical aspects of the feature are missing\n\n"
        "Subtasks to validate:\n{subtasks}\n\n"
        "If any issues are found, provide specific recommendations for improvement."
    ),
}
