from pathlib import Path
import subprocess

def get_file_list(repo_path: str):
    """Get the list of files in the repository, ignoring .gitignore files"""
    # Use git command to list files not ignored by .gitignore
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_path,
        text=True,
        capture_output=True,
        check=True
    )
    files = result.stdout.splitlines()
    return [Path(repo_path) / file for file in files]