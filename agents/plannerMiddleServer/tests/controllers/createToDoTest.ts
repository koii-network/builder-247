import { startServer } from "../../src/app";
import { connectToDatabase } from "../../src/app";
import axios from "axios";

async function main() {
	startServer();
	await connectToDatabase();
	try {
		const response = await axios.post(
			"http://localhost:3000/api/create-to-do",
			{
				title: "Sample ToDo",
				acceptanceCriteria: "Criteria for acceptance",
				repoOwner: "OwnerName",
				repoName: "RepoName",
			}
		);
		console.log("Response:", response.data);
	} catch (error) {
		console.error(error);
	}
}

main();
