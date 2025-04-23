"""Prompts for the repository summarization workflow."""

PROMPTS = {
    "system_prompt": (
        "You are an expert software architect and technical lead specializing in summarizing "
        "repositories into comprehensive documentation. You excel at analyzing codebases "
        "and creating clear, structured documentation."
    ),
    "create_branch": (
        "You need to create a feature branch for the README generation.\n"
        "Create a new branch with a descriptive name related to creating a README file.\n"
    ),
    "classify_repository": (
        "Analyze the repository structure and identify the type of repository this is.\n"
        "Use the `classify_repository` tool to report your choice.\n"
        "You must choose one of the following repository types:\n"
        "- Library/SDK: Code meant to be imported and used by other developers\n"
        "- Web App: Frontend or full-stack web application\n"
        "- API Service: Server-side application providing APIs\n"
        "- Mobile App: Native or cross-platform mobile app\n"
        "- Tutorial: Educational repository demonstrating techniques\n"
        "- Template: Starter code for new projects\n"
        "- CLI Tool: Command-line interface application\n"
        "- Framework: Foundational structure for building applications\n"
        "- Data Science: Machine learning or data analysis project\n"
        "- Plugin: Extension or module for a larger system (e.g., CMS, IDE, platform)\n"
        "- Chrome Extension: Browser extension targeting the Chrome platform\n"
        "- Jupyter Notebook: Interactive code notebooks, often for demos or research\n"
        "- Infrastructure: Configuration or automation code (e.g., Docker, Terraform)\n"
        "- Smart Contract: Blockchain smart contracts, typically written in Solidity, Rust, etc.\n"
        "- DApp: Decentralized application with both smart contract and frontend components\n"
        "- Game: Codebase for a game or game engine (2D, 3D, or browser-based)\n"
        "- Desktop App: GUI application for desktop environments (e.g., Electron, Qt, Tauri)\n"
        "- Dataset: Repository containing structured data for analysis or training\n"
        "- Other: If it doesn't fit into any of the above categories\n"
        "IMPORTANT: Do not assume that the README is correct. "
        "Classify the repository based on the codebase.\n"
        "If files are mentioned in the README but are not present in the codebase, "
        "do NOT use them as a source of information.\n"
    ),
    "generate_readme_section": (
        "You are writing the {section_name} section of a README file for a repository.\n"
        "The readme will contain the following sections:\n"
        "{all_sections}\n"
        "Restrict your documentation to the section you are writing.\n"
        "Read all files relevant to your task and generate comprehensive, clear documentation.\n"
        "The section should include the following information:\n"
        "{section_description}\n"
        "Write the section in markdown format.\n"
        "The section name will be automatically added as a second level heading.\n"
        "Do not include the section name in your documentation.\n"
        "Any sub-sections should be added as third level headings.\n"
        "IMPORTANT: Do not assume that an existing README is correct. "
        "Create the documentation based on the codebase.\n"
        "If files are mentioned in the README but are not present in the codebase, "
        "do NOT reference them in your documentation.\n"
        "If a section is not relevant to the repository, just return an empty string.\n"
    ),
    "generate_readme": (
        "Create a descriptive title for the following README contents and create the README file:\n"
        "{readme_content}\n"
        "The content will be added automatically, your job is just to create a good title."
    ),
    "create_pr": (
        "You are creating a pull request for the documentation you have generated:\n"
        "IMPORTANT: Always use relative paths (e.g., 'src/file.py' not '/src/file.py')\n\n"
        "Steps to create the pull request:\n"
        "1. First examine the available files to understand the implementation\n"
        "2. Create a clear and descriptive PR title\n"
        "3. Write a comprehensive PR description that includes:\n"
        "   - Description of all changes made\n"
        "   - The main features and value of the documentation\n"
    ),
    "review_readme_file": (
        "Review the README_Prometheus.md file in the repository and evaluate its quality and "
        "relevance to the repository.\n\n"
        "Please analyze:\n"
        "1. Is the README_Prometheus.md file related to this specific repository? (Does it describe the actual code "
        "and purpose of this repo?)\n"
        "2. Does it correctly explain the repository's purpose, features, and functionality?\n"
        "3. Is it comprehensive enough to help users understand and use the repository?\n"
        "4. Does it follow best practices for README documentation?\n\n"
        "Use the validate_implementation tool to submit your findings.\n"
        "IMPORTANT: Do not assume that an existing README is correct. "
        "Evaluate README_Prometheus.md against the codebase.\n"
        "STOP after submitting the review report."
    ),
    "previous_review_comments": ("Here are the comments from the previous review:\n"),
}
