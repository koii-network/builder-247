# Merge Conflict Resolver Workflow

This workflow is designed to automatically detect and resolve merge conflicts in GitHub repositories. It can handle merging individual branches or multiple pull requests in order, resolving conflicts as they arise using the existing git operations tools.

## Features

- Detects merge conflicts between source and target branches using Git directly
- Intelligently resolves conflicts by understanding the changes from both branches
- Can merge multiple PRs in order (oldest first), resolving conflicts as needed
- Provides detailed information about each conflict and its resolution
- Uses specialized Git tools to ensure proper conflict resolution without breaking the merge process

## Usage

### As a Python Module

```python
from src.workflows.mergeconflict import MergeConflictWorkflow, PROMPTS

# Initialize the workflow for a specific branch
workflow = MergeConflictWorkflow(
    client=client,  # Claude client
    prompts=PROMPTS,
    repo_url="https://github.com/owner/repo",
    target_branch="main",
    source_branch="feature-branch",
)

# Or initialize for merging all PRs
workflow = MergeConflictWorkflow(
    client=client,  # Claude client
    prompts=PROMPTS,
    repo_url="https://github.com/owner/repo",
    target_branch="main",
    merge_all_prs=True,
)

# Run the workflow
result = workflow.run()

# Check the result for a specific branch
if result["success"]:
    print(f"Successfully resolved {len(result['data']['resolved_conflicts'])} conflicts")
else:
    print(f"Failed to resolve conflicts: {result['message']}")

# Check the result for merging all PRs
if result["success"]:
    print(f"Successfully merged {len(result['data']['merged_prs'])} PRs")
    if result["data"]["failed_prs"]:
        print(f"Failed to merge {len(result['data']['failed_prs'])} PRs")
else:
    print(f"Failed to merge PRs: {result['message']}")
```

### Command-Line Interface

You can also run the workflow directly from the command line:

```bash
# Set up environment variables (or use a .env file)
export ANTHROPIC_API_KEY=your_api_key
export GITHUB_TOKEN=your_github_token
export GITHUB_USERNAME=your_github_username

# Merge a specific branch
python -m src.workflows.mergeconflict \
    --repo-url https://github.com/owner/repo \
    --source-branch feature-branch \
    --target-branch main

# Merge a specific PR
python -m src.workflows.mergeconflict \
    --repo-url https://github.com/owner/repo \
    --pr-number 123 \
    --target-branch main

# Merge all open PRs in order (oldest first)
python -m src.workflows.mergeconflict \
    --repo-url https://github.com/owner/repo \
    --target-branch main \
    --merge-all-prs
```

Command-line options:

- `--repo-url`: URL of the GitHub repository (required)
- `--target-branch`: Name of the target branch to merge into (required)
- `--source-branch`: Name of the source branch with changes to merge
- `--pr-number`: PR number if resolving conflicts in a specific PR
- `--merge-all-prs`: Flag to merge all open PRs targeting the target branch in order (oldest first)
- `--api-key`: Anthropic API key (optional, can also be set via ANTHROPIC_API_KEY environment variable)

## Workflow Process

The workflow follows a streamlined process:

1. **Conflict Detection**: Uses Git directly to detect conflicts when merging branches
2. **Conflict Resolution**: Resolves the detected conflicts intelligently using Claude AI and specialized Git tools
3. **Merge Completion**: Creates a merge commit after all conflicts are resolved

## Merging Multiple PRs

When using the `--merge-all-prs` option or setting `merge_all_prs=True` in the constructor, the workflow will:

1. Get all open PRs targeting the specified target branch
2. Sort them by creation date (oldest first)
3. For each PR:
   - Try to merge the PR branch into the target branch
   - If there are no conflicts, commit the merge
   - If there are conflicts, use Git to detect them and Claude to resolve them
   - If the merge is successful, continue to the next PR
   - If the merge fails, stop the process

## Git Operations Tools Used

The workflow uses the following git operations tools directly:

- `check_for_conflicts`: Checks for merge conflicts in the current repository
- `get_conflict_info`: Retrieves detailed information about each conflict
- `resolve_conflict`: Resolves a conflict in a specific file by writing the resolution and staging the file (does not create a commit)
- `create_merge_commit`: Creates a merge commit after all conflicts are resolved and staged

## Requirements

- GitHub token with appropriate permissions
- GitHub username
- Anthropic API key
- Access to the repository
