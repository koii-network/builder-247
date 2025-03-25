"""Prompts for the repository summarization workflow."""

PROMPTS = {
    "system_prompt": (
        "You are an expert software architect and technical lead specializing in summarizing "
        "repositories into comprehensive documentation. You excel at analyzing codebases "
        "and creating clear, structured documentation."
    ),
    
    "check_readme_file": (
        "A pull request has been checked out for you. The repository is {repo_owner}/{repo_name} and "
        "the PR number is {pr_number}. The following files are available:\n"
        "{current_files}\n\n"
        "The criteria for the README file are:\n"
        "1. Project Overview\n"
        "   - Purpose and main functionality\n"
        "   - Key features\n"
        "2. Repository Structure\n"
        "   - Detailed breakdown of directories and their purposes\n"
        "   - Key files and their roles\n"
        "3. Technical Details\n"
        "   - Technologies used\n"
        "   - Architecture overview\n"
        "4. File Contents\n"
        "   - Specific description of each significant file\n\n"
        "Please review the README file and give feedback.\n"
    ),

}
