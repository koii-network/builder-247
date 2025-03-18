import { Request, Response } from "express";
import { TodoModel } from "../models/Todo";

export const getIssuePrUrls = async (req: Request, res: Response) => {
  const { issueUuid } = req.params;
  const todos = await TodoModel.find({ issueUuid });
  const prUrls = todos.map((todo) => todo.assignedTo.find((assigned) => assigned.auditResult === true)?.prUrl);
  res.json(prUrls);
};




