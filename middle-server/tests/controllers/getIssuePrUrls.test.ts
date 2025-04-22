import { TodoModel } from "../../src/models/Todo";
import app from "../../src/app";
import request from "supertest";
import mongoose from "mongoose";
import { describe, beforeAll, beforeEach, afterAll, it, expect } from "@jest/globals";

describe("getIssuePrUrls", () => {
  beforeAll(async () => {
    // Connect to test database
    await mongoose.connect(process.env.MONGODB_URI as string);
  });

  afterAll(async () => {
    await mongoose.connection.close();
  });

  beforeEach(async () => {
    // Clear the todos collection before each test
    await TodoModel.deleteMany({});
  });

  it("should return PR URLs for todos with matching issueUuid", async () => {
    // Create sample todos in the database
    const issueUuid = "test-issue-123";
    const sampleTodos = [
      {
        title: "Todo 1",
        uuid: "todo-1",
        issueUuid: issueUuid,
        description: "Test description",
        acceptanceCriteria: "Test criteria",
        repoOwner: "test-owner",
        repoName: "test-repo",
        assignedTo: [
          {
            stakingKey: "staking-key-1",
            pubkey: "pub-key-1",
            taskId: "task-1",
            roundNumber: 1,
            githubUsername: "user1",
            prUrl: "https://github.com/test/pr/1",
            auditResult: true,
          },
        ],
        status: "in_progress",
      },
      {
        title: "Todo 2",
        uuid: "todo-2",
        issueUuid: issueUuid,
        description: "Test description 2",
        acceptanceCriteria: "Test criteria 2",
        repoOwner: "test-owner",
        repoName: "test-repo",
        assignedTo: [
          {
            stakingKey: "staking-key-2",
            pubkey: "pub-key-2",
            taskId: "task-2",
            roundNumber: 1,
            githubUsername: "user2",
            prUrl: "https://github.com/test/pr/2",
            auditResult: true,
          },
        ],
        status: "in_progress",
      },
    ];

    await TodoModel.insertMany(sampleTodos);

    // Make the request
    const response = await request(app).get(`/api/builder/get-issue-pr-urls/${issueUuid}`);

    // Assertions
    expect(response.status).toBe(200);
    expect(response.body).toEqual(["https://github.com/test/pr/1", "https://github.com/test/pr/2"]);
  });

  it("should return empty array when no todos found", async () => {
    const nonExistentIssueUuid = "non-existent-issue";

    const response = await request(app).get(`/api/builder/get-issue-pr-urls/${nonExistentIssueUuid}`);

    expect(response.status).toBe(200);
    expect(response.body).toEqual([]);
  });
});
