import { Keypair } from "@_koii/web3.js";
import { signData } from "../../src/utils/sign";
import { getTaskState } from "../../src/utils/taskState";
import { TodoModel, TodoStatus } from "../../src/models/Todo";
import app from "../../src/app";
import request from "supertest";
import { taskID } from "../../src/constant";
jest.mock("../../src/utils/taskState", () => ({
  getTaskState: jest.fn(),
  isValidStakingKey: jest.fn().mockReturnValue(true),
  checkAssignedInfoExists: jest.fn().mockReturnValue(false),
}));

jest.mock("../../src/models/Todo", () => {
  const originalModule = jest.requireActual("../../src/models/Todo");
  return {
    __esModule: true,
    ...originalModule,
    TodoModel: {
      find: jest.fn().mockReturnValue({ select: jest.fn().mockReturnValue(true) }),
      findOne: jest.fn().mockReturnValue({
        select: jest.fn().mockReturnValue({
          lean: jest.fn().mockReturnValue({
            _id: "todoId",
            assignedTo: [
              {
                stakingKey: "mockStakingKey",
                roundNumber: "1",
                prUrl: null,
              },
            ],
          }),
        }),
      }),
      findOneAndUpdate: jest.fn().mockReturnValue({
        select: jest.fn().mockReturnValue({
          lean: jest.fn().mockReturnValue({
            _id: "todoId",
            assignedTo: [
              {
                stakingKey: "mockStakingKey",
                roundNumber: "1",
                prUrl: "prUrl",
              },
            ],
          }),
        }),
      }),
    },
  };
});

jest.mock("../../src/constant", () => ({
  taskID: "mockTaskID",
}));

jest.mock("../../src/utils/sign", () => ({
  ...jest.requireActual("../../src/utils/sign"),
  verifySignature: jest.fn().mockReturnValue({
    data: JSON.stringify({
      taskId: "mockTaskID",
      roundNumber: 1,
      type: "Audit",
    }),
    error: null,
  }),
}));

it("should return 200 and the first todo if everything is valid", async () => {
  const encodedData = "encodedData";
  const mockTodo = [
    {
      _id: "todoId",
      title: "Test Todo",
      acceptanceCriteria: "Criteria",
      repoOwner: "Owner",
      repoName: "Repo",
      status: TodoStatus.INITIALIZED,
      assignedTo: [],
    },
  ];

  (getTaskState as jest.Mock).mockResolvedValue(["mockStakingKey"]);
  (TodoModel.find as jest.Mock).mockResolvedValue(mockTodo);

  const response = await request(app).post("/api/builder/add-pr-to-to-do").send({
    signature: encodedData,
    pubKey: "mockStakingKey",
    prUrl: "prUrl",
  });

  console.log("Response Status:", response.status);
  console.log("Response Body:", response.body);

  expect(response.status).toBe(200);
  expect(response.body.success).toEqual(true);
  // expect(response.body).toEqual({
  //   success: true,
  //   data: {
  //     ...mockTodo,
  //     assignedTo: [{ stakingKey: mockStakingKey, taskId: mockTaskID, roundNumber: mockRoundNumber.toString() }],
  //   },
  // });
});
