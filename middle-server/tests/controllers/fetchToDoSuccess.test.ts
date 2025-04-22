// import { Keypair } from "@_koii/web3.js";
// import { signData } from "../../src/utils/sign";
// import { getTaskState } from "../../src/utils/taskState";
// import { TodoModel, TodoStatus } from "../../src/models/Todo";
// import app from "../../src/app";
// import request from "supertest";
// import { taskID } from "../../src/constant";
// import { isValidStakingKey } from "../../src/utils/taskState";
// jest.mock("../../src/utils/taskState", () => ({
//   getTaskState: jest.fn(),
//   isValidStakingKey: jest.fn().mockReturnValue(true),
//   checkAssignedInfoExists: jest.fn().mockReturnValue(false),
// }));

// jest.mock("../../src/models/Todo", () => {
//   const originalModule = jest.requireActual("../../src/models/Todo");
//   const { TodoStatus } = originalModule;
//   return {
//     __esModule: true,
//     ...originalModule,
//     TodoModel: {
//       find: jest.fn().mockImplementation(() => ({
//         sort: jest.fn().mockReturnThis(),
//         select: jest.fn().mockReturnThis(),
//         lean: jest.fn().mockResolvedValue([
//           {
//             _id: "65d9a7d9c4b8c45b4f3e3d9c",
//             title: "Test Todo",
//             status: originalModule.TodoStatus.INITIALIZED,
//             assignedTo: [],
//             createdAt: new Date(),
//             updatedAt: new Date(),
//             __v: 0,
//           },
//         ]),
//       })),
//       findOne: jest.fn().mockImplementation(() => ({
//         select: jest.fn().mockReturnThis(),
//         lean: jest.fn().mockResolvedValue(null),
//       })),
//       findOneAndUpdate: jest.fn().mockImplementation(() => ({
//         lean: jest.fn().mockResolvedValue({
//           _id: "65d9a7d9c4b8c45b4f3e3d9c",
//           title: "Test Todo",
//           status: originalModule.TodoStatus.INITIALIZED,
//           assignedTo: [
//             {
//               stakingKey: "mockStakingKey",
//               taskId: "mockTaskID",
//               roundNumber: 1,
//               githubUsername: "github_username",
//             },
//           ],
//           createdAt: new Date(),
//           updatedAt: new Date(),
//           __v: 1,
//         }),
//       })),
//     },
//   };
// });

// jest.mock("../../src/constant", () => ({
//   taskID: "mockTaskID",
// }));

// it("should return 200 and the first todo if everything is valid", async () => {
//   const mockKeypair = Keypair.generate();
//   const mockTaskID = taskID;
//   const mockRoundNumber = 1;
//   const mockStakingKey = mockKeypair.publicKey.toBase58();
//   const data = {
//     taskId: mockTaskID,
//     roundNumber: mockRoundNumber.toString(),
//   };

//   let encodedData: string;
//   try {
//     console.log("Mock Keypair:", mockKeypair);
//     console.log("Data:", data);
//     encodedData = await signData(mockKeypair, data);
//     console.log("Encoded Data after signData call:", encodedData);
//   } catch (error) {
//     console.error("Error signing data:", error);
//     return;
//   }

//   const mockTodo = {
//     _id: "65d9a7d9c4b8c45b4f3e3d9c",
//     title: "Test Todo",
//     acceptanceCriteria: "Criteria",
//     repoOwner: "Owner",
//     repoName: "Repo",
//     status: TodoStatus.INITIALIZED,
//     assignedTo: [],
//     createdAt: new Date(),
//     updatedAt: new Date(),
//     __v: 0,
//   };

//   (getTaskState as jest.Mock).mockResolvedValue([mockStakingKey]);
//   (TodoModel.find as jest.Mock).mockImplementation(() => ({
//     sort: jest.fn().mockReturnThis(),
//     select: jest.fn().mockReturnThis(),
//     lean: jest.fn().mockResolvedValue([mockTodo]),
//   }));

//   (TodoModel.findOne as jest.Mock).mockImplementation(() => ({
//     select: jest.fn().mockReturnThis(),
//     lean: jest.fn().mockResolvedValue(null),
//   }));

//   (TodoModel.findOneAndUpdate as jest.Mock).mockImplementationOnce(() => ({
//     lean: jest.fn().mockResolvedValue({
//       _id: "65d9a7d9c4b8c45b4f3e3d9c",
//       title: "Test Todo",
//       assignedTo: [
//         {
//           stakingKey: mockStakingKey,
//           taskId: mockTaskID,
//           roundNumber: 1,
//           githubUsername: "github_username",
//         },
//       ],
//       createdAt: new Date(),
//       updatedAt: new Date(),
//       __v: 1,
//     }),
//   }));

//   const response = await request(app).post("/api/builder/fetch-to-do").send({
//     signature: encodedData,
//     pubKey: mockStakingKey,
//     github_username: "github_username",
//   });

//   console.log("Response Status:", response.status);
//   console.log("Response Body:", response.body);

//   expect(response.status).toBe(200);
//   // expect(response.body.data).toMatchObject({
//   //   _id: "65d9a7d9c4b8c45b4f3e3d9c",
//   //   title: "Test Todo",
//   //   assignedTo: expect.arrayContaining([
//   //     expect.objectContaining({
//   //       stakingKey: mockStakingKey,
//   //       taskId: mockTaskID
//   //     })
//   //   ])
//   // });
//   // expect(response.body.data.assignedTo).toHaveLength(1);
//   // expect(TodoModel.findOneAndUpdate).toHaveBeenCalledWith(
//   //   {
//   //     _id: "todoId",
//   //     $expr: { $lt: [{ $size: "$assignedTo" }, 2] }
//   //   },
//   //   {
//   //     $push: {
//   //       assignedTo: expect.objectContaining({
//   //         stakingKey: mockStakingKey,
//   //         taskId: mockTaskID
//   //       })
//   //     }
//   //   },
//   //   { new: true }
//   // );
// });
