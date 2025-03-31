"""Prompts for the repository summarization workflow."""

PROMPTS = {
    "system_prompt": (
        "You are an expert software architect and technical lead specializing in summarizing "
        "repositories into comprehensive documentation. You excel at analyzing codebases "
        "and creating clear, structured documentation."
    ),
    
    "generate_readme_file": (
        "Generate a comprehensive README file for the following repository:\n"
        "Repository: {repo_url}\n\n"
        "Please include:\n"
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
        "Format the output in markdown, ensuring clear section headers and proper formatting."
        "Please commit and push the changes to the repository after generating the README file."
    ),

}
