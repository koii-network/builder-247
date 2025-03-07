# Earn Crypto with AI Agents: Prometheus 24/7 Builder Task (Beta v0)

## Overview

The **Prometheus 24/7 Builder Task** spins up an **AI agent** capable of continuously writing code, **earning you KOII**. Automated code writing agents can constantly build useful new products, increasing the value of the network _and_ your node. Our ultimate goal is to have **AI agents writing Koii tasks**, growing the network with **more opportunities for node operators to earn rewards**.

## Releases

### Beta v0

- This is the **first beta release** of the task.
- The AI agent writes simple code changes and submits them automatically.
- Code is sent to the **[Prometheus Beta repository](https://github.com/koii-network/prometheus-beta)**.
- Future versions will introduce **enhanced AI logic, more complex coding tasks, and more!**

## Task Setup

**[How to set up a Claude API key and a GitHub API key for the 247 Builder Task.](https://www.koii.network/blog/Earn-Crypto-With-AI-Agent)**

## How It Works

1. The Koii Node **launches an AI agent** inside a lightweight runtime.
2. The agent reads an active **to-do list** from the repository.
3. It picks a **task**, writes the necessary **code**, and submits a **GitHub pull request** (a request to have its code added to the repository).
4. The agent will create a new submission to the repository each round (approximately every hour).
5. Koii Nodes **earn rewards** for running the AI agent and contributing code.

# Merge Conflict Resolution Scripts

This repository contains scripts for automatically merging pull requests and resolving merge conflicts using AI. The scripts use Claude to intelligently resolve merge conflicts.

## Prerequisites

Before using these scripts, make sure you have the following:

1. Python 3.7 or higher
2. Required Python packages (install with `pip install -r requirements.txt`):
   - PyGithub
   - python-dotenv
   - anthropic
3. Environment variables:
   - `GITHUB_TOKEN`: A GitHub personal access token with repo permissions
   - `GITHUB_USERNAME`: Your GitHub username
   - `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude
4. GitHub CLI (`gh`) installed and authenticated

## Scripts

### Merge Conflicts Script

The `merge_conflicts.py` script is a simplified tool that merges a source branch into a target branch, resolving any conflicts that arise using Claude AI.

```bash
python merge_conflicts.py \
    --repo-url https://github.com/owner/repo \
    --source-branch feature-branch \
    --target-branch main
```

Options:

- `--repo-url`: URL of the GitHub repository (required)
- `--source-branch`: Name of the source branch with changes to merge (required)
- `--target-branch`: Name of the target branch to merge into (default: main)
- `--api-key`: Anthropic API key (can also be set via ANTHROPIC_API_KEY environment variable)
- `--dry-run`: Perform a dry run without actually resolving conflicts
- `--clone-dir`: Directory to clone the repository into (default: ./repo_clone)

## How It Works

1. The script clones the repository to a local directory
2. It fetches the source and target branches
3. It attempts to merge the source branch into the target branch
4. If conflicts are detected:
   - It uses Claude to analyze and resolve each conflict
   - It creates a new branch with the resolved conflicts
   - It pushes the branch to GitHub
   - It creates a pull request for the resolved conflicts
5. If no conflicts are detected, it simply reports that the merge was successful

## Example Usage

### Merge a feature branch into main

```bash
python merge_conflicts.py --repo-url https://github.com/owner/repo --source-branch feature-branch
```

### Perform a dry run to check for conflicts

```bash
python merge_conflicts.py --repo-url https://github.com/owner/repo --source-branch feature-branch --dry-run
```

### Specify a custom clone directory

```bash
python merge_conflicts.py --repo-url https://github.com/owner/repo --source-branch feature-branch --clone-dir ./my_repo
```
