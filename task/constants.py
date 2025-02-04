PROMPTS = {
    "setup_repository": "Please create a new branch and switch to it in the repository located at {repo_path}. Ensure that this branch fully addresses the task described by: {todo}", 
    "generic_acceptance_criteria" :"Please make sure the tests, controllers, routes, are under different folders. Please make sure the tests pass. Please make sure the code is modular and readable.", 
    "files": "Below is the list of files in the repository: {files}. Remember every command you run is on the base directory. Please use the command 'cd example_repo' for every command you want to run in the repo Path.",
    "commit": "Please commit using the {repo_path} as repo_path. The information is {todo}",
    "push": "Please push using the {repo_path} as repo_path.",
    "create_pr": "Please create a pull request with the following details: todo {todo}, repo full name {repo_full_name}, head {head}, base {base}; You have to include [x] I have tested my changes in the checklist."
}