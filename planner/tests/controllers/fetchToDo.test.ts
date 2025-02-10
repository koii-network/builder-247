import request from "supertest";
import { app, startServer } from "../../src/app";
import { verifySignature } from "../../src/utils/sign";
jest.mock("../../src/utils/sign");
jest.mock("../../src/utils/taskState");
jest.mock("../../src/models/Todo");

let server: any;

beforeAll(() => {
  server = startServer();
});

afterAll((done) => {
  server.close(done);
});

describe("fetchTodo", () => {
  it("should return 401 if signature verification fails", async () => {
    (verifySignature as jest.Mock).mockResolvedValue({
      error: `Failed to verify signature`,
    });

    const response = await request(app)
      .get("/api/fetch-to-do")
      .query({
        signature: "invalid",
        pubKey: "key",
        github_username: "invalid",
      });

    expect(response.status).toBe(401);
    expect(response.body.success).toEqual(false);
    expect(response.body.message).toEqual("Failed to verify signature");
  });

  it("should return 401 if request body is invalid", async () => {
    const response = await request(app).get("/api/fetch-to-do").query({});

    expect(response.status).toBe(401);
    expect(response.body).toEqual({
      success: false,
      message: "Invalid request body",
    });
  });
});
