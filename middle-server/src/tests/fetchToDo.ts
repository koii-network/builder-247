// import { fetchTodo, fetchTodoLogic } from "../controllers/api/builder/fetchToDo";
// import { Keypair } from "@_koii/web3.js";
// import { signData } from "../utils/sign";
// import mongoose from "mongoose";
// import dotenv from "dotenv";

// dotenv.config();

// const testFetchTodo = async () => {
//   await mongoose.connect(process.env.MONGODB_URI!);
//   const returnValue = await fetchTodoLogic(
//     { signature: "fakesignature", stakingKey: "fakestakingkey", pubKey: "fakepubkey" },
//     { roundNumber: 1, githubUsername: "sss" },
//   );
//   console.log(returnValue);
// };

// testFetchTodo();

// /****
//  * Returned Value:
//  * {
//     statuscode: 200,
//     data: {
//         success: true,
//         role: 'aggregator',
//         issue_uuid: '456e7890-e12b-34d5-f678-526614174111',
//         assignPendingIssueUUIDs: []
//     }
// }
//  */
