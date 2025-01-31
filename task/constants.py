PROMPTS = {
    "setup_repository": "Please create a new branch and switch to it in the repository located at ${repo_path}. Ensure that this branch fully addresses the task described by: ${todo}", 
    "files": "Below is the list of files in the repository: {files}. To navigate to the repository path, please use the command 'cd test'.",
    "commit_push_create_pr": "Please create a pull request with the following details: todo {todo}, repo full name {repo_full_name}, head {head}, base {base}"
    
}