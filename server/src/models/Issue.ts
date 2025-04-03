import { prop, getModelForClass, modelOptions, Severity } from "@typegoose/typegoose";

modelOptions({
  schemaOptions: {
    timestamps: true,
  },
  options: {
    allowMixed: Severity.ALLOW,
  },
});

enum IssueStatus {
  INITIALIZED = "initialized",
  AGGREGATOR_PENDING = "aggregator_pending",
  IN_PROGRESS = "in_progress",
  ASSIGN_PENDING = "assign_pending", // Means awaiting assignment to a leader node
  ASSIGNED = "assigned", // Means assigned to a leader node
  IN_REVIEW = "in_review", // Means a PR is opened and waiting for review
  APPROVED = "approved", // Means a PR passed audit and appeared on the distribution list
  MERGED = "merged", // Means a PR is merged manually
}

class Issue {
  @prop({ required: true })
  public issueUuid!: string;

  @prop({ required: false })
  public title?: string;

  @prop({ required: false })
  public description?: string;

  @prop({ required: true })
  public repoOwner!: string;

  @prop({ required: true })
  public repoName!: string;

  @prop({ required: false })
  public aggregatorOwner?: string;

  @prop({ required: false })
  public aggregatorUrl?: string;

  @prop({ required: false })
  public assignedStakingKey?: string;

  @prop({ required: false })
  public assignedGithubUsername?: string;

  @prop({ required: false })
  public assignedRoundNumber?: number;

  @prop({ required: false })
  public prUrl?: string;

  @prop({ required: true, enum: IssueStatus, default: IssueStatus.INITIALIZED })
  public status!: IssueStatus;
}

const IssueModel = getModelForClass(Issue);
export { Issue, IssueModel, IssueStatus };
