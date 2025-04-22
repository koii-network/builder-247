// import { addIssuePRLogic } from "../controllers/api/builder/addIssuePR";
// import { Keypair } from "@_koii/web3.js";
// import { signData } from "../utils/sign";
// import mongoose from "mongoose";
// import dotenv from "dotenv";

// dotenv.config();

// const testAddIssuePR = async () => {
//   await mongoose.connect(process.env.MONGODB_URI!);
//   const returnValue = await addIssuePRLogic(
//     { signature: "fakesignature", stakingKey: "fakestakingkey", pubKey: "fakepubkey" },
//     {
//       roundNumber: 1,
//       prUrl: "https://github.com/koii-network/koii-core/pull/1234",
//       issueUuid: "456e7890-e12b-34d5-f678-526614174111",
//     },
//   );
//   console.log(returnValue);
// };

// testAddIssuePR();
