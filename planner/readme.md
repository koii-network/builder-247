# API Usage

## /fetch-to-do

Request: `{signautre: string, pubKey: string, github_username: string}`
Signature: `signature` is signed `{taskId: string, roundNumber: string}`

## /add-pr-to-to-do

Request: `{signautre: string, pubKey: string, githubPullRequestUrl: string}`
Signature: `signature` is signed `{taskId: string, roundNumber: string, type:"Audit"}`

## /create-to-do

Request: `{title:string, acceptanceCriteria:string, repoOwner:string, repoName:string}`
