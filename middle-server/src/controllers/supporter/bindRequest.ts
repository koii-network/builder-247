import { Request, Response } from "express";
import { StarFollowModel } from "../../models/StarFollow";

export const bindRequest = async (req: Request, res: Response) => {
    try {
        const { stakingKey, githubId, githubUsername, issueNumber } = req.body;

        // Initialize Octokit
        const { Octokit } = await import('@octokit/rest');
        const octokit = new Octokit({
            auth: process.env.GITHUB_TOKEN,
        });

        // Check if stakin

        // 1. Verify GitHub username matches GitHub ID
        try {
            const { data: user } = await octokit.users.getByUsername({ username: githubUsername });
            if (user.id.toString() !== githubId) {
                res.status(400).json({
                    success: false,
                    message: "GitHub username does not match the provided GitHub ID"
                });
                return;
            }
        } catch (error) {
            res.status(400).json({
                success: false,
                message: "Invalid GitHub username or ID"
            });
            return;
        }

        // 2. Check if stakingKey matches in the issue
        // get issue body 
        const issueData = await octokit.issues.get({
            owner: "koii-network",
            repo: "StarAndFollowSupportRepo",
            issue_number: issueNumber
        });
        const issueBody = issueData.data.body;
        if (!issueBody) {
            res.status(400).json({
                success: false,
                message: "Issue body not found"
            });
            return;
        }
        const issueBodyJson = JSON.parse(issueBody);
        if (issueBodyJson.stakingKey !== stakingKey) {
            res.status(400).json({
                success: false,
                message: "Staking key does not match the issue"
            });
            return;
        }

        // 3. Check if GitHub ID already exists in the database
        const existingStarFollow = await StarFollowModel.findOne({ gitHubId: githubId });
        if (existingStarFollow ) {
            if (existingStarFollow.stakingKey === stakingKey) {
                res.status(201).json({
                    success: true,
                    message: "Successfully bound request",
                    data: existingStarFollow
                });
                return;
            }else{
                res.status(400).json({
                    success: false,
                    message: "GitHub ID already exists in the database"
                });
                return;
            }
        }

        // Create new entry in the database
        const newStarFollow = await StarFollowModel.create({
            gitHubId: githubId,
            stakingKey: stakingKey,
            gitHubUsername: githubUsername,
            status: "initialized"
        });

        res.status(200).json({
            success: true,
            message: "Successfully bound request",
            data: newStarFollow
        });
        return;
    } catch (error) {
        console.error("Error in bindRequest:", error);
        res.status(500).json({
            success: false,
            message: "Internal server error"
        });
        return;
    }
};

