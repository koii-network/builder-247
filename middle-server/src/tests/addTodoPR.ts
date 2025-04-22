// import { addPRLogic } from "../controllers/api/builder/addTodoPR";
// import { Keypair } from "@_koii/web3.js";
// import { signData } from "../utils/sign";
// import mongoose from "mongoose";
// import dotenv from "dotenv";

// dotenv.config();

// const testAddTodoPR = async () => {
//   await mongoose.connect(process.env.MONGODB_URI!);
//   const returnValue = await addPRLogic(
//     { signature: "fakesignature", stakingKey: "fakestakingkey", pubKey: "fakepubkey" },
//     { roundNumber: 1, prUrl: "https://github.com/koii-network/koii-core/pull/1234" },
//   );
//   console.log(returnValue);
// };

// testAddTodoPR();
