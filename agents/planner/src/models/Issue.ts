import { prop, getModelForClass, modelOptions, Severity } from "@typegoose/typegoose";

modelOptions({
  schemaOptions: {
    timestamps: true,
  },
  options: {
    allowMixed: Severity.ALLOW,
  },
})

enum IssueStatus {
  INITIALIZED = "initialized",
  ASSIGN_PENDING = "assign_pending", // Means assigned to a leader node
  IN_REVIEW = "in_review", // Means a PR is opened and waiting for review
  MERGED = "merged",// Means a PR is merged manually
}

class Issue {
  @prop({ required: true })
  public issueUuid!: string;

  @prop({ required: true, enum: IssueStatus, default: IssueStatus.INITIALIZED })
  public status!: IssueStatus;

  @prop({ required: false })
  public leaderNodeStakingKey!: string;

  @prop({ required: false })
  public leaderNodeMergeRound!: number;

  @prop({ required: false })
  public leaderNodeMergeTaskId!: string;

  @prop({ required: false })
  public leaderNodeMergeTaskSignature!: string;
}

const IssueModel = getModelForClass(Issue);
export { Issue, IssueModel, IssueStatus };
