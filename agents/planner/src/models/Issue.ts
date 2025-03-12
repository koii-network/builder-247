import { prop, getModelForClass, modelOptions, Severity } from "@typegoose/typegoose";

class AssignedInfo {
  @prop({ required: true })
  public issueUuid!: string;

  @prop({ required: true })
  public status!: string;
}

enum TodoStatus {
  INITIALIZED = "initialized",
  DONE = "done",
}

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
  AUDIT_PENDING = "audit_pending",
  IN_REVIEW = "in_review",
  MERGED = "merged",
}

class Todo {
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

const TodoModel = getModelForClass(Todo);
export { Todo, TodoModel, TodoStatus, AssignedInfo };
