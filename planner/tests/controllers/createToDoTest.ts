import { startServer } from "../../src/app";
import { connectToDatabase } from "../../src/app";
import axios from "axios";

async function main() {
  startServer();
  await connectToDatabase();
  try {
    const response = await axios.get("http://localhost:3000/api/create-to-do", {
      params: {
        title: "Sample ToDo",
        acceptanceCriteria: "Criteria for acceptance",
        repoOwner: "OwnerName",
        repoName: "RepoName",
      },
    });
    console.log("Response:", response.data);
  } catch (error) {
    console.error(error);
  }
}

main();
