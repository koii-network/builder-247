"""Script to analyze and generate a detailed summary of the repository using the Anthropic API."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv(project_root / ".env")

from src.client import AnthropicClient

# Import filesystem tools
def list_dir(relative_workspace_path: str) -> str:
    """List contents of a directory."""
    path = Path(relative_workspace_path)
    if not path.exists():
        return f"Directory {relative_workspace_path} does not exist"
    return "\n".join(sorted(os.listdir(path)))

def read_file(relative_workspace_path: str, should_read_entire_file: bool = False) -> str:
    """Read contents of a file."""
    path = Path(relative_workspace_path)
    if not path.exists():
        return f"File {relative_workspace_path} does not exist"
    with open(path) as f:
        return f.read()

def grep_search(query: str) -> str:
    """Search for patterns in files."""
    import subprocess
    try:
        result = subprocess.run(["grep", "-r", query, "."], capture_output=True, text=True)
        return result.stdout or "No matches found"
    except subprocess.CalledProcessError:
        return "Error running grep search"

def file_search(query: str) -> str:
    """Search for files by name."""
    import subprocess
    try:
        result = subprocess.run(["find", ".", "-name", f"*{query}*"], capture_output=True, text=True)
        return result.stdout or "No files found"
    except subprocess.CalledProcessError:
        return "Error running file search"

def codebase_search(query: str) -> str:
    """Semantic search across the codebase."""
    # For now, just use grep as a simple implementation
    return grep_search(query)

def main():
    """Main function to analyze repository and generate summary."""
    # Initialize client
    client = AnthropicClient()
    
    print("Starting repository analysis...")
    
    # Track tools used and their responses across phases
    tools_used = []
    tool_responses = []
    
    # Helper function to record tool usage
    def record_tool_usage(name: str, args: dict, response: str):
        tools_used.append({"name": name, "args": args})
        # Format response nicely and truncate if too long
        response = response[:1000] if len(response) > 1000 else response
        formatted_response = f"\n=== {name} output ===\n{response}\n==================\n"
        tool_responses.append(formatted_response)
    
    # First, explore repository structure
    print("Phase 1: Exploring repository structure...")
    
    # Get root directory contents
    root_contents = list_dir(".")
    record_tool_usage("list_dir", {"relative_workspace_path": "."}, root_contents)
    
    # Find key files
    readme_files = file_search("README")
    record_tool_usage("file_search", {"query": "README"}, readme_files)
    
    # Read key files
    if "README.md" in root_contents:
        readme_content = read_file("README.md", should_read_entire_file=True)
        record_tool_usage("read_file", {"relative_workspace_path": "README.md"}, readme_content)
    
    # Send first prompt with gathered info
    explore_prompt = """You are a powerful AI assistant with direct access to filesystem tools. You have ALREADY used these tools to gather information about the repository:

1. Used list_dir(".") to get the repository structure
2. Used file_search("README") to find key files
3. Used read_file("README.md") to read its contents

The tool outputs are shown above. Please analyze them to understand:
- Project purpose and goals from README.md
- Main components and structure from directory listing
- Development status from available files

You have these tools available RIGHT NOW to explore further:
- list_dir: Lists contents of a directory
- read_file: Reads contents of a file
- grep_search: Searches for patterns in files
- file_search: Searches for files by name
- codebase_search: Semantic search across the codebase

Please use these tools to gather any additional information you need. Start by analyzing the outputs above, then use more tools to explore anything that needs clarification."""
    
    structure_response = client.send_message(explore_prompt, tools_used=tools_used, tool_responses=tool_responses)
    print("Structure analysis complete.")
    
    # Clear tool history before next phase
    tools_used.clear()
    tool_responses.clear()
    
    # Next, analyze contents in detail
    print("Phase 2: Analyzing repository contents...")
    
    # Search for specific patterns
    functions = grep_search("def ")
    record_tool_usage("grep_search", {"query": "def "}, functions)
    
    classes = grep_search("class ")
    record_tool_usage("grep_search", {"query": "class "}, classes)
    
    # Look for tests
    test_files = file_search("test")
    record_tool_usage("file_search", {"query": "test"}, test_files)
    
    # Check src directory
    src_contents = list_dir("src")
    record_tool_usage("list_dir", {"relative_workspace_path": "src"}, src_contents)
    
    analyze_prompt = """Now let's analyze the repository in detail. I've gathered additional information.
Please analyze the tool outputs above to understand:

1. Functions and classes defined (from grep_search)
2. Testing infrastructure (from file_search)
3. Source code organization (from list_dir)

Focus on:
- Code architecture and patterns
- Testing approach and coverage
- Key functionality and features

You can use additional tools if needed."""
    
    analysis_response = client.send_message(analyze_prompt, tools_used=tools_used, tool_responses=tool_responses)
    print("Content analysis complete.")
    
    # Finally, generate comprehensive summary
    print("Phase 3: Generating comprehensive summary...")
    summarize_prompt = """Based on all the information we've gathered using the filesystem tools, please generate a comprehensive markdown summary.

You have access to:
1. Repository structure and files (from list_dir/file_search)
2. Code organization and patterns (from grep_search/codebase_search)
3. Documentation and tests (from read_file)
4. Development status (from todo.md)

Please create a detailed summary with:

1. Project Overview
   - Purpose and goals (from README)
   - Key features (from code)
   - Tech stack (from dependencies)

2. Architecture & Design
   - Code organization (from structure)
   - Design patterns (from code)
   - Key components (from search)

3. Key Features & Functionality
   - Core features (from docs/code)
   - APIs and integrations (from code)
   - Tools and utilities (from search)

4. Testing & Quality Assurance
   - Testing approach (from tests)
   - Test coverage (from analysis)
   - Quality metrics (from config)

5. Development Process
   - Workflow (from docs)
   - Tools and automation (from config)
   - Documentation (from comments)

6. Current Status & Roadmap
   - Completed features (from todo)
   - Ongoing work (from branches)
   - Future plans (from roadmap)

Use specific examples and details from the tool outputs above."""
    
    summary_response = client.send_message(summarize_prompt, tools_used=tools_used, tool_responses=tool_responses)
    print("Summary generation complete.")
    
    # Save the summary to testing/review.md
    output_dir = Path("testing")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "review.md", "w") as f:
        f.write(summary_response)
    
    print(f"Summary saved to {output_dir}/review.md")

if __name__ == "__main__":
    main() 