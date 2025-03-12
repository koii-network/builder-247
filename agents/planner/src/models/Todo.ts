import { prop, getModelForClass, modelOptions, Severity } from "@typegoose/typegoose";

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

enum TodoStatus {
  INITIALIZED = "initialized",
  DONE = "done",
}

@modelOptions({
  schemaOptions: {
    timestamps: true,
  },
  options: {
    allowMixed: Severity.ALLOW,
  },
})
class Todo {
  @prop({ required: true })
  public title!: string;

  @prop({ required: true })
  public uuid!: string;

  @prop({ required: true })
  public issueUuid!: string;

  @prop({ required: true })
  public description!: string;

  @prop({ required: true })
  public acceptanceCriteria!: string;

  @prop({ required: true })
  public repoOwner!: string;

  @prop({ required: true })
  public repoName!: string;

  @prop({ type: () => [AssignedInfo], default: [] })
  public assignedTo!: AssignedInfo[];

  @prop({
    enum: TodoStatus,
    default: TodoStatus.INITIALIZED,
    required: true,
  })
  public status!: TodoStatus;
}

const TodoModel = getModelForClass(Todo);
export { Todo, TodoModel, TodoStatus, AssignedInfo };
