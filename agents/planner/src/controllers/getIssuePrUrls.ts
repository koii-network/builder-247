import { Request, Response } from "express";
import { TodoModel } from "../models/Todo";

export const getIssuePrUrls = async (req: Request, res: Response) => {
  try {
    const { issueUuid } = req.params;
    console.log(`Searching todos for issue UUID: ${issueUuid}`);
    
    const todos = await TodoModel.find({ issueUuid });
    console.log(`Found ${todos.length} todos for issue UUID: ${issueUuid}`);

    if (!todos || todos.length === 0) {
      console.log(`No todos found for issue UUID: ${issueUuid}`);
      res.status(404).json({
        success: false,
        message: `No todos found for issue UUID: ${issueUuid}`,
        data: null
      });
      return;
    }

    const prUrls = todos.map((todo) => todo.assignedTo.find((assigned) => assigned.auditResult === true)?.prUrl)
      .filter(url => url !== undefined);
    console.log(`Found ${prUrls.length} PR URLs for issue UUID: ${issueUuid}`);

    res.status(200).json({
      success: true,
      message: "PR URLs retrieved successfully",
      data: prUrls
    });
  } catch (error) {
    console.error('Error in getIssuePrUrls:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while fetching PR URLs',
      data: null
    });
  }
};




