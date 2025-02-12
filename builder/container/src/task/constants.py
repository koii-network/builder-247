PROMPTS = {
    "setup_repository": "Please create a new branch off main and give it a name that describes the task: {todo}",
    "files": "Below is the list of files in the repository: {files}.",
    "commit": "Please make a commit with a descriptive message. "
    "Give the commit a message that describes the task: {todo}",
    "push": "Please push the changes to the remote repository.",
    "create_pr": "Please create a pull request with the following details: todo {todo}, repo full name "
    "{repo_full_name}, head {head}, base {base}. "
    "You have to include '[x] I have tested my changes' (without the quotes) in the checklist.",
}
