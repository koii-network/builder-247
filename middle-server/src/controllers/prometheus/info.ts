import { DocumentationModel } from "../../models/Documentation";
import { Request, Response } from "express";
import { DocumentationStatus } from "../../models/Documentation";



import { SwarmBountyStatus, SwarmBountyType } from "../../config/constant";
import { getLastRoundValueLength } from "../../utils/taskState/activeNode";
export const info = async (req: Request, res: Response) => {
  const { swarmBountyId, swarmType } = req.query;

  if (!swarmBountyId || !swarmType) {
    res.status(400).json({ error: "swarmBountyId and swarmType are required" });
    return;
  }
  const validTypes = Object.values(SwarmBountyType);
  if (!validTypes.includes(swarmType as any)) {
    res.status(400).json({ error: "Invalid swarm type" });
    return;
  }
  if (swarmType === SwarmBountyType.DOCUMENT_SUMMARIZER) {
    const { statuscode, data } = await getDocumentationInfo(swarmBountyId as string);
    res.status(statuscode).json(data);
    return;
  }
  if (swarmType === SwarmBountyType.FIND_BUGS) {
    const { statuscode, data } = await getFindBugsInfo(swarmBountyId as string);
    res.status(statuscode).json(data);
    return;
  }
  if (swarmType === SwarmBountyType.BUILD_FEATURE) {
    const { statuscode, data } = await getBuildFeatureInfo(swarmBountyId as string);
    res.status(statuscode).json(data);
    return;
  }
  res.status(500).json({ error: "Internal server error" });
  return;

};
// @dummy function
export const getFindBugsInfo = async (swarmsBountyId: string): Promise<{ statuscode: number; data: any }> => {
    return {
        statuscode: 200,
        data: {
            success: true,
            data: {
                issues: 0,
                nodes: 0,
                status: SwarmBountyStatus.IN_PROGRESS
            }
        }
    }
}

export const getBuildFeatureInfo = async (swarmsBountyId: string): Promise<{ statuscode: number; data: any }> => {
    return {
        statuscode: 200,
        data: {
            success: true,
            data: {
                issues: 0,
                nodes: 0,
                status: SwarmBountyStatus.IN_PROGRESS
            }
        }
    }
}
export const getDocumentationNumberOfNodesTemp = async (): Promise<number> => {
  const documentationTaskId = process.env.DOCUMENT_SUMMARIZER_TASK_ID;
  if (!documentationTaskId) {
      throw new Error("DOCUMENTATION_TASK_ID is not set");
  }
  const numberOfNodes = await getLastRoundValueLength(documentationTaskId);
  return numberOfNodes;
}
export const getDocumentationInfo = async (swarmsBountyId: string): Promise<{ statuscode: number; data: any }> => {
    try {
      console.log("swarmsBountyId", swarmsBountyId);
      const documentation = await DocumentationModel.findOne({ swarmBountyId: swarmsBountyId });
      console.log("documentation", documentation);
      if (documentation && documentation.assignedTo) {
        const numberOfNodes = await getDocumentationNumberOfNodesTemp();
        let status; 
        if (documentation.status === DocumentationStatus.IN_PROGRESS) {
          if (documentation.assignedTo.length === 0) {
            status = SwarmBountyStatus.IN_PROGRESS;
          } else {
            if (documentation.assignedTo[documentation.assignedTo.length - 1].prUrl) {
              if (documentation.assignedTo[documentation.assignedTo.length - 1].auditResult==true) {
                status = SwarmBountyStatus.COMPLETED;
              } else {
                status = SwarmBountyStatus.AUDITING;
              }
            } else {
              status = SwarmBountyStatus.ASSIGNED;
            }
          }
        }
        return {
          statuscode: 200,
          data: {
            success: true,
            data: {
                issues: 1,
                nodes: numberOfNodes,
                status: documentation.status
            }
          },
        };
      }
      return {
        statuscode: 409,
        data: {
          success: false,
          message: "Documentation not found",
        },
      };
    } catch (error) {
      console.log("error", error);
      return {
        statuscode: 500,
        data: {
          success: false,
          message: "Error getting assigned to in documentation",
        },
      };
    }
};
  


