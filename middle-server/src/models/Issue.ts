import { prop, getModelForClass, modelOptions, Severity } from "@typegoose/typegoose";
import { builder247DB } from "../services/database/database";

enum IssueStatus {
  INITIALIZED = "initialized",
  AGGREGATOR_PENDING = "aggregator_pending",
  IN_PROGRESS = "in_progress",
  ASSIGN_PENDING = "assign_pending", // Awaiting assignment to a leader node
  ASSIGNED = "assigned", // Assigned to a leader node
  IN_REVIEW = "in_review", // The PR is opened and waiting for review
  APPROVED = "approved", // The PR passed audit and appeared on the distribution list
  MERGED = "merged", // The PR is merged (must be done manually by bounty owner)
}

class AssignedInfo {
  @prop({ required: true })
  public stakingKey!: string;

  @prop({ required: true })
  public githubUsername!: string;
  @prop({ required: true })
  public roundNumber!: number;

  @prop({ required: false })
  public approved?: boolean;

  @prop({ required: false })
  public failedAuditReason?: string;

  @prop({ required: false })
  public failedAuditFeedback?: string;

  @prop({ required: false })
  public prUrl?: string;
}

@modelOptions({
  schemaOptions: {
    timestamps: true,
  },
  options: {
    allowMixed: Severity.ALLOW,
  },

  existingConnection: builder247DB,
})
class Issue {
  @prop({ required: true })
  public issueUuid!: string;

  @prop({ required: true })
  public taskId!: string;

  @prop({ required: false })
  public title?: string;

  @prop({ required: false })
  public description?: string;

  @prop({ required: true })
  public repoOwner!: string;

  @prop({ required: false })
  public swarmBountyId?: string;

  @prop({ required: true })
  public repoName!: string;

  @prop({ required: false })
  public aggregatorOwner?: string;

  @prop({ required: false })
  public aggregatorUrl?: string;

  @prop({ required: false })
  public assignees?: AssignedInfo[];

  @prop({ required: true, enum: IssueStatus, default: IssueStatus.INITIALIZED })
  public status!: IssueStatus;
}

const IssueModel = getModelForClass(Issue);
export { Issue, IssueModel, IssueStatus, AssignedInfo };
