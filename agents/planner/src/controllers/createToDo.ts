import { Request, Response } from "express";
import { TodoModel } from "../models/Todo";
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
