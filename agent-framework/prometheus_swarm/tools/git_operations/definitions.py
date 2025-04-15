from prometheus_swarm.tools.git_operations.implementations import (
    init_repository,
    clone_repository,
    create_branch,
    checkout_branch,
    commit_and_push,
    get_current_branch,
    list_branches,
    add_remote,
    fetch_remote,
    pull_remote,
    can_access_repository,
    check_for_conflicts,
    get_conflict_info,
    resolve_conflict,
    create_merge_commit,
)

DEFINITIONS = {
    "init_repository": {
        "name": "init_repository",
        "description": "Initialize a new Git repository with optional user configuration.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path where to initialize the repository",
                },
                "user_name": {
                    "type": "string",
                    "description": "Git user name to configure",
                },
                "user_email": {
                    "type": "string",
                    "description": "Git user email to configure",
                },
            },
            "required": ["path"],
        },
        "function": init_repository,
    },
    "clone_repository": {
        "name": "clone_repository",
        "description": "Clone a Git repository with proper path handling and cleanup.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL of the repository to clone",
                },
                "path": {
                    "type": "string",
                    "description": "Path where to clone the repository",
                },
                "user_name": {
                    "type": "string",
                    "description": "Git user name to configure",
                },
                "user_email": {
                    "type": "string",
                    "description": "Git user email to configure",
                },
            },
            "required": ["url", "path"],
        },
        "function": clone_repository,
    },
    "create_branch": {
        "name": "create_branch",
        "description": "Create a new branch with automatic timestamp suffix.",
        "parameters": {
            "type": "object",
            "properties": {
                "branch_base": {
                    "type": "string",
                    "description": "Base name for the branch",
                },
            },
            "required": ["branch_base"],
        },
        "function": create_branch,
    },
    "checkout_branch": {
        "name": "checkout_branch",
        "description": "Check out an existing branch in the current repository.",
        "parameters": {
            "type": "object",
            "properties": {
                "branch_name": {
                    "type": "string",
                    "description": "Name of the branch to checkout",
                },
            },
            "required": ["branch_name"],
        },
        "function": checkout_branch,
    },
    "commit_and_push": {
        "name": "commit_and_push",
        "description": "Commit all changes and push to remote.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Commit message"},
            },
            "required": ["message"],
        },
        "function": commit_and_push,
    },
    "get_current_branch": {
        "name": "get_current_branch",
        "description": "Get the current branch name in the working directory.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
        "function": get_current_branch,
    },
    "list_branches": {
        "name": "list_branches",
        "description": "List all branches in the current repository.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
        "function": list_branches,
    },
    "add_remote": {
        "name": "add_remote",
        "description": "Add a remote to the current repository.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the remote"},
                "url": {"type": "string", "description": "URL of the remote"},
            },
            "required": ["name", "url"],
        },
        "function": add_remote,
    },
    "fetch_remote": {
        "name": "fetch_remote",
        "description": "Fetch from a remote in the current repository.",
        "parameters": {
            "type": "object",
            "properties": {
                "remote_name": {
                    "type": "string",
                    "description": "Name of the remote to fetch from",
                },
            },
            "required": ["remote_name"],
        },
        "function": fetch_remote,
    },
    "pull_remote": {
        "name": "pull_remote",
        "description": "Pull changes from a remote branch.",
        "parameters": {
            "type": "object",
            "properties": {
                "remote_name": {"type": "string", "description": "Name of the remote"},
                "branch": {"type": "string", "description": "Branch to pull from"},
            },
        },
        "function": pull_remote,
    },
    "can_access_repository": {
        "name": "can_access_repository",
        "description": "Check if a git repository is accessible.",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_url": {
                    "type": "string",
                    "description": "URL of the repository to check",
                },
            },
            "required": ["repo_url"],
        },
        "function": can_access_repository,
    },
    "check_for_conflicts": {
        "name": "check_for_conflicts",
        "description": "Check for merge conflicts in the current repository.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
        "function": check_for_conflicts,
    },
    "get_conflict_info": {
        "name": "get_conflict_info",
        "description": "Get details about current conflicts from Git's index.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
        "function": get_conflict_info,
    },
    "resolve_conflict": {
        "name": "resolve_conflict",
        "description": "Resolve a conflict in a specific file.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file with conflicts",
                },
                "resolution": {
                    "type": "string",
                    "description": "Content to resolve the conflict with",
                },
            },
            "required": ["file_path", "resolution"],
        },
        "function": resolve_conflict,
    },
    "create_merge_commit": {
        "name": "create_merge_commit",
        "description": "Create a merge commit after resolving conflicts.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Commit message for the merge",
                },
            },
            "required": ["message"],
        },
        "function": create_merge_commit,
    },
}
