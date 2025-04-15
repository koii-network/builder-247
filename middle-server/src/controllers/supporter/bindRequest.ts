import { Request, Response } from "express";
import { StarFollowModel } from "../../models/StarFollow";

export const bindRequest = async (req: Request, res: Response) => {
    try {
        const { stakingKey, githubId, githubUsername, issue } = req.body;

        // Initialize Octokit
        const { Octokit } = await import('@octokit/rest');
        const octokit = new Octokit({
            auth: process.env.GITHUB_TOKEN,
        });

        // 1. Verify GitHub username matches GitHub ID
        try {
            const { data: user } = await octokit.users.getByUsername({ username: githubUsername });
            if (user.id.toString() !== githubId) {
                return res.status(400).json({
                    success: false,
                    message: "GitHub username does not match the provided GitHub ID"
                });
            }
        } catch (error) {
            return res.status(400).json({
                success: false,
                message: "Invalid GitHub username or ID"
            });
        }

        // 2. Check if stakingKey matches in the issue
        if (issue.stakingKey !== stakingKey) {
            return res.status(400).json({
                success: false,
                message: "Staking key does not match the issue"
            });
        }

        // 3. Check if GitHub ID already exists in the database
        const existingStarFollow = await StarFollowModel.findOne({ gitHubId: githubId });
        if (existingStarFollow) {
            return res.status(400).json({
                success: false,
                message: "GitHub ID already exists in the database"
            });
        }

        // Create new entry in the database
        const newStarFollow = await StarFollowModel.create({
            gitHubId: githubId,
            stakingKey: stakingKey,
            gitHubUsername: githubUsername,
            status: "initialized"
        });

        return res.status(200).json({
            success: true,
            message: "Successfully bound request",
            data: newStarFollow
        });

    } catch (error) {
        console.error("Error in bindRequest:", error);
        return res.status(500).json({
            success: false,
            message: "Internal server error"
        });
    }
};

