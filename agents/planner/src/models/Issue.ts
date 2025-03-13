import { prop, getModelForClass, modelOptions, Severity } from "@typegoose/typegoose";

modelOptions({
  schemaOptions: {
    timestamps: true,
  },
  options: {
    allowMixed: Severity.ALLOW,
  },
})
class AssignedInfo {
  @prop({ required: true })
  public stakingKey!: string;

  @prop({ required: true })
  public pubkey!: string;

  @prop({ required: true })
  public taskId!: string;

  @prop({ required: true })
  public roundNumber!: number;

  @prop({ required: true })
  public githubUsername!: string;

  @prop({ required: false })
  public prUrl?: string;

  @prop({ required: false })
  public todoSignature?: string;

  @prop({ required: false })
  public prSignature?: string;

  @prop({ required: false })
  public auditSignature?: string;

  @prop({ required: false })
  public auditResult?: boolean;
}

class AggregatorInfo {
  @prop({ required: true })
  public stakingKey!: string;

  @prop({ required: true })
  public githubUsername!: string;

  @prop({ required: true })
  public roundNumber!: number;
}
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
  public title?: string;

  @prop({ required: false })
  public description?: string;

  @prop({ required: true })
  public repoOwner!: string;

  @prop({ required: true })
  public repoName!: string;
  
  @prop({ required: true })
  public aggregator!: AggregatorInfo;


  @prop({ required: false, type: () => [AssignedInfo], default: [] })
  public assignedTo!: AssignedInfo[];
}

const IssueModel = getModelForClass(Issue);
export { Issue, IssueModel, IssueStatus };
