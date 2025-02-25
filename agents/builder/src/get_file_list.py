from git import Repo


def get_file_list(repo_path: str):
    """Get the list of tracked files in the repository using GitPython, excluding .git directories."""
    try:
        repo = Repo(repo_path)
        # Get list of tracked files (relative paths)
        files = [item[0] for item in repo.index.entries.keys()]
        # Filter out .git directories and __pycache__
        return [f for f in files if not (f.startswith(".git/") or "__pycache__" in f)]
    except Exception as e:
        print(f"Error getting file list: {str(e)}")
        return []
