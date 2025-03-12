"""Prompts for the merge conflict resolver workflow."""

PROMPTS = {
    "system_prompt": (
        "You are an expert software architect and technical lead specializing in resolving merge conflicts "
        "and consolidating changes from multiple pull requests. You understand software development best "
        "practices and focus on maintaining code quality while resolving conflicts."
    ),
    "resolve_conflicts": (
        "You need to resolve merge conflicts in the following files. For each conflict:\n"
        "1. Analyze both versions of the code\n"
        "2. Understand the intent of each change\n"
        "3. Determine how to combine the changes while preserving functionality\n"
        "4. Ensure the resolution maintains code quality and follows project conventions\n\n"
        "Guidelines for conflict resolution:\n"
        "- Preserve the intent of both changes when possible\n"
        "- Maintain consistent code style\n"
        "- Ensure the resolution doesn't introduce new bugs\n"
        "- Add comments to explain complex resolutions\n"
        "- Consider implications for other parts of the codebase\n\n"
        "Current repository state:\n{current_files}\n\n"
    ),
    "create_consolidated_pr": (
        "Create a pull request that consolidates changes from multiple worker PRs.\n\n"
        "Context:\n"
        "- Source Fork: {source_fork}\n"
        "- Working Fork: {working_fork}\n"
        "- Upstream Repo: {upstream}\n"
        "- Merged PRs: {merged_prs}\n\n"
        "Guidelines for PR creation:\n"
        "- Title should clearly indicate this is a consolidation PR\n"
        "- Description should list all merged PRs\n"
        "- Use the leader PR template\n"
        "- Target the upstream repository's default branch\n"
    ),
    "decompose_feature": (
        "Your task is to break down the following feature request into small, discrete subtasks:\n\n"
        "Feature: {feature_description}\n"
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
        "- Account for documentation needs\n\n"
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
