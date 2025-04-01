import { prop, getModelForClass, modelOptions, Severity } from "@typegoose/typegoose";

enum TodoStatus {
  // Means not assigned to any node
  // This  can also be used when a node is audited as false, so we can reassign it to another node
  INITIALIZED = "initialized",
  // Means is assigned to a node, not completed
  // This can be used when the node does not complete a task, so we can reassign it to another node
  IN_PROGRESS = "in_progress",
  IN_REVIEW = "in_review", // PR has been submitted but no audit yet
  APPROVED = "approved", // Means a PR passed audit and appeared on the distribution list
  MERGED = "merged", // Means a PR is merged
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
  public taskId!: string;

  @prop({ required: true })
  public description!: string;

  @prop({ required: true, type: () => [String] })
  public acceptanceCriteria!: string[];

  @prop({ required: true })
  public repoOwner!: string;

  @prop({ required: true })
  public repoName!: string;

  @prop({ required: false })
  public assignedStakingKey?: string;

  @prop({ required: false })
  public assignedGithubUsername?: string;

  @prop({ required: false })
  public assignedRoundNumber?: number;

  @prop({ required: false })
  public prUrl?: string;

  @prop({ type: () => [String], default: [] })
  public dependencyTasks!: string[];

  @prop({
    enum: TodoStatus,
    default: TodoStatus.INITIALIZED,
    required: true,
  })
  public status!: TodoStatus;
}

const TodoModel = getModelForClass(Todo);
export { Todo, TodoModel, TodoStatus };
