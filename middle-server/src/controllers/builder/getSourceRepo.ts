import { Request, Response } from "express";
import { IssueModel } from "../../models/Issue";
import { TodoModel } from "../../models/Todo";
export const getSourceRepo = async (req: Request, res: Response) => {
  try {
    const { uuid, nodeType } = req.params;
    if (nodeType === "leader") {
      const issue = await IssueModel.findOne({ issueUuid: uuid }).select("repoOwner repoName");
      if (!issue) {
        return res.status(409).json({
          success: false,
          message: "Issue not found",
          data: null,
        });
      }
      return res.status(200).json({
        success: true,
        message: "Issue found",
        data: issue,
      });
    } else {
      const todo = await TodoModel.findOne({ uuid }).select("repoOwner repoName");
      if (!todo) {
        return res.status(409).json({
          success: false,
          message: "Todo not found",
          data: null,
        });
      }
      return res.status(200).json({
        success: true,
        message: "Todo found",
        data: todo,
      });
    }
  } catch (error) {
    console.error("Error in getIssuePrUrls:", error);
    res.status(500).json({
      success: false,
      message: "Internal server error while fetching PR URLs",
      data: null,
    });
  }
};
