from git import Repo


def get_file_list(repo_path: str):
    """Get the list of tracked files in the repository using GitPython."""
    try:
        repo = Repo(repo_path)
        # Get list of tracked files (relative paths)
        return [item[0] for item in repo.index.entries.keys()]
    except Exception as e:
        print(f"Error getting file list: {str(e)}")
        return []
