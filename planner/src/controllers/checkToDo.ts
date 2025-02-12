import { Request, Response } from "express";
import { TodoModel } from "../models/Todo";
import { verifySignature } from "../utils/sign";
import { taskID } from "../constant";
import { isValidStakingKey } from "../utils/taskState";

// Helper function to verify request body
function verifyRequestBody(req: Request): {
	signature: string;
	pubKey: string;
	github_username: string;
	prUrl: string;
} | null {
	try {
		const signature = req.body.signature as string;
		const pubKey = req.body.pubKey as string;
		const github_username = req.body.github_username as string;
		const prUrl = req.body.prUrl as string;
		if (!signature || !pubKey || !github_username || !prUrl) {
			return null;
		}
		return { signature, pubKey, github_username, prUrl };
	} catch {
		return null;
	}
}

// Helper function to verify signature
async function verifySignatureData(
	signature: string,
	pubKey: string
): Promise<{ roundNumber: string } | null> {
	try {
		const { data, error } = await verifySignature(signature, pubKey);
		console.log("Decoded Data:", data);
		console.log("Decoded Error:", error);
		if (error || !data) {
			return null;
		}
		const body = JSON.parse(data);
		console.log("Decoded JSON Body:", body);
		console.log("TaskID comparison:", {
			bodyTaskId: body.taskId,
			constantTaskId: taskID,
			bodyTaskIdType: typeof body.taskId,
			constantTaskIdType: typeof taskID,
		});

		if (
			!body.taskId ||
			!body.roundNumber ||
			body.taskId !== taskID ||
			body.action !== "check"
		) {
			return null;
		}
		return { roundNumber: body.roundNumber };
	} catch (error) {
		console.error("Error in verifySignatureData:", error);
		return null;
	}
}

async function checkToDoAssignment(
	stakingKey: string,
	roundNumber: string,
	githubUsername: string,
	prUrl: string
): Promise<boolean> {
	try {
		const result = await TodoModel.findOne({
			assignedTo: {
				$elemMatch: {
					stakingKey: stakingKey,
					roundNumber: roundNumber,
					githubUsername: githubUsername,
					githubPullRequestUrl: prUrl,
					taskId: taskID,
				},
			},
		}).lean();

		console.log("Todo assignment check result:", result);
		return result !== null;
	} catch (error) {
		console.error("Error checking todo assignment:", error);
		return false;
	}
}

export const checkToDo = async (req: Request, res: Response) => {
	const requestBody = verifyRequestBody(req);
	if (!requestBody) {
		res.status(401).json({
			success: false,
			message: "Invalid request body",
		});
		return;
	}

	const signatureData = await verifySignatureData(
		requestBody.signature,
		requestBody.pubKey
	);
	if (!signatureData) {
		res.status(401).json({
			success: false,
			message: "Failed to verify signature",
		});
		return;
	}

	if (!(await isValidStakingKey(requestBody.pubKey))) {
		res.status(401).json({
			success: false,
			message: "Invalid staking key",
		});
		return;
	}

	const isValid = await checkToDoAssignment(
		requestBody.pubKey,
		signatureData.roundNumber,
		requestBody.github_username,
		requestBody.prUrl
	);

	if (!isValid) {
		res.status(404).json({
			success: false,
			message: "No matching todo assignment found",
		});
		return;
	}

	res.status(200).json({
		success: true,
		message: "Todo assignment verified successfully",
	});
};
