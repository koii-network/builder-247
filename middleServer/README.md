# API Usage

## /fetch-to-do

Request: `{signature: string, pubKey: string, github_username: string}`
Signature: `signature` is signed `{taskId: string, roundNumber: string, action: "fetch"}`

## /add-pr

Request: `{signature: string, pubKey: string, prUrl: string}`
Signature: `signature` is signed `{taskId: string, roundNumber: string, action: "add"}`

## /check-to-do

Request: `{signature: string, pubKey: string, github_username: string, prUrl: string}`
Signature: `signature` is signed `{taskId: string, roundNumber: string, action: "check"}`

## /create-to-do

Request: `{title:string, acceptanceCriteria:string, repoOwner:string, repoName:string}`
