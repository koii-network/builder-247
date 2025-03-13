import { Request, Response } from "express";
import { TodoModel, TodoStatus } from "../models/Todo";
import mongoose from "mongoose";
import dotenv from "dotenv";

dotenv.config();
// @ this is a testing only endpoint
export const createTodo = async (req: Request, res: Response) => {
	const { title, acceptanceCriteria, repoOwner, repoName } = req.body;
	const todo = new TodoModel({
		title,
		acceptanceCriteria,
		repoOwner,
		repoName,
	});
	await todo.save();
	res.status(201).json({ todo });
};

export const insertMultipleExampleTodos = async () => {
	await mongoose.connect(process.env.MONGODB_URI as string);
	const exampleTodo = new TodoModel({
		title: "Implement new feature",
		uuid: "123e4567-e89b-12d3-a456-426614174000",
		issueUuid: "456e7890-e12b-34d5-f678-526614174111",
		description: "This task involves implementing a new feature in the application.",
		acceptanceCriteria: "The feature should be fully functional and pass all tests.",
		repoOwner: "exampleOwner",
		repoName: "exampleRepo",
		dependencyTasks: ["task1", "task2"],
		status: TodoStatus.INITIALIZED,
	  });
	  await exampleTodo.save();
	  console.log("Example todo inserted");

};

insertMultipleExampleTodos();