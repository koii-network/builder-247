PROMPTS = {
    "setup_repository": "Please create a new branch off main and switch to it in the "
    "repository located at {repo_path}. Give the branch a name that describes the task: {todo}",
    "files": "Below is the list of files in the repository: {files}. Remember every command you run is on the base "
    "directory. Please use the command 'cd {repo_path}' for every command you want to run in the repo Path.",
    "commit": "Please commit using the {repo_path} as repo_path. "
    "Give the commit a message that describes the task: {todo}",
    "push": "Please push using the {repo_path} as repo_path.",
    "create_pr": "Please create a pull request with the following details: todo {todo}, repo full name "
    "{repo_full_name}, head {head}, base {base}. "
    "You have to include '[x] I have tested my changes' (without the quotes) in the checklist.",
}
