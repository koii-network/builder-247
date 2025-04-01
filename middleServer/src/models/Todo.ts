import { prop, getModelForClass, modelOptions, Severity } from "@typegoose/typegoose";
import { builder247DB } from "../utils/database";
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
  // Means not assigned to any node
  // This  can also be used when a node is audited as false, so we can reassign it to another node
  INITIALIZED = "initialized", 
  // Means is assigned to a node, not completed
  // This can be used when the node does not complete a task, so we can reassign it to another node
  IN_PROGRESS = "in_progress", 
  AUDITED = "audited", // Means a PR is audited and waiting for merge
  MERGED = "merged", // Means a PR is merged
}

@modelOptions({
  schemaOptions: {
    timestamps: true,
  },
  options: {
    allowMixed: Severity.ALLOW,
  },
  existingConnection: builder247DB
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
export { Todo, TodoModel, TodoStatus, AssignedInfo };

