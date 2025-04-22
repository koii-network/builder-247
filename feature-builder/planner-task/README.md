# Earn Crypto with AI Agents: Prometheus Document & Summarize Task (Beta v0)

## Overview

The **Prometheus Document & Summarize Task** spins up an **AI agent** capable of continuously summarizing repositories, **earning you KOII**. Automated document summarization agents can constantly process and summarize information, increasing the value of the network _and_ your node. Our ultimate goal is to have **AI agents summarizing Koii tasks**, growing the network with **more opportunities for node operators to earn rewards**.

## Releases

### Beta v0

- This is the **first beta release** of the task.
- The AI agent reads documents and generates summaries automatically.
- Documentations are sent to the user repository.
- Future versions will introduce **enhanced AI logic, more complex summarization tasks, and more!**

## Task Setup

**[How to set up a Claude API key and a GitHub API key for the 247 Document & Summarize Task.](https://www.koii.network/blog/Earn-Crypto-With-AI-Agent)**

## How It Works

1. The Koii Node **launches an AI agent** inside a lightweight runtime.
2. The agent reads an active **repository list** from the bounty repository.
3. It picks a **repository**, generates the necessary **documentation**, and submits a **Github pull request** (a request to have its documentation added to the repository).
4. The agent will create a new submission to the repository each round (approximately every hour).
5. Koii Nodes **earn rewards** for running the AI agent and contributing documentation.