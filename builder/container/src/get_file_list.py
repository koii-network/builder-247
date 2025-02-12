from pathlib import Path
from git import Repo


def get_file_list(repo_path: str):
    """Get the list of tracked files in the repository using GitPython."""
    try:
        repo = Repo(repo_path)
        files = [item[0] for item in repo.index.entries.keys()]  # Get path from tuple
        return [Path(repo_path) / file for file in files]
    except Exception as e:
        print(f"Error getting file list: {str(e)}")
        return []
