import { Request, Response } from "express";
import { TodoModel } from "../models/Todo";

export const createTodo = async (req: Request, res: Response) => {
  const { title, acceptanceCriteria, repoOwner, repoName } = req.query;
  const todo = new TodoModel({
    title,
    acceptanceCriteria,
    repoOwner,
    repoName,
  });
  await todo.save();
  res.status(201).json({ todo });
};
