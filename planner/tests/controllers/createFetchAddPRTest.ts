// Set src/utils/taskState.ts as validate staking keys true
import { startServer, connectToDatabase } from "../../src/app";
import axios from "axios";
import { Keypair } from "@_koii/web3.js";
import { signData } from "../../src/utils/sign";

async function test() {
	const server = await startServer();
	await connectToDatabase();
	// Example of creating a todo:
	// const response = await axios.post("http://localhost:3000/api/create-to-do", {
	//   title: "test",
	//   acceptanceCriteria: "test",
	//   repoOwner: "test",
	//   repoName: "test"
	// });
	// console.log(response.data);

	const taskId = "tempSimulateTaskID";
	const roundNumber = "1";
	const notSignedData = { taskId, roundNumber };
	const keypair = Keypair.generate();
	const signature = await signData(keypair, notSignedData);
	const pubKey = keypair.publicKey.toBase58();
	const githubUsername = "mockGithubUsername";

	try {
		const response2 = await axios.post(
			"http://localhost:3000/api/fetch-to-do",
			{
				signature,
				pubKey,
				github_username: githubUsername,
			}
		);
		console.log(response2.data);
	} catch (error) {
		console.log(error);
	}

	const notSignedData3 = { taskId, roundNumber, type: "Audit" };
	const signature3 = await signData(keypair, notSignedData3);
	const prUrl = "https://github.com/koii-network/koii-core/pull/1234";
	console.log("1111111");

	try {
		const response3 = await axios.post(
			"http://localhost:3000/api/add-pr-to-to-do",
			{
				signature: signature3,
				pubKey,
				prUrl,
			}
		);
		console.log(response3.data);
	} catch (error) {
		console.log(error);
	}
}

test();
