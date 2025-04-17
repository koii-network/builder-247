import { prop, getModelForClass, modelOptions, Severity } from '@typegoose/typegoose';
import { builder247DB } from '../services/database/database';

enum TodoStatus {
  INITIALIZED = 'initialized', // Not yet assigned to a node. Reset to this if anything goes wrong
  IN_PROGRESS = 'in_progress', // Is assigned to a node, not completed
  IN_REVIEW = 'in_review', // PR has been submitted but no audit yet
  APPROVED = 'approved', // PR passed audit and appeared on the distribution list
  MERGED = 'merged', // PR is merged by leader node
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
  public failedReason?: string;

  @prop({ required: false })
  public failedFeedback?: string;

  @prop({ required: false })
  public recoverableFailure?: boolean;

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
class Todo {
  @prop({ required: true })
  public title!: string;

  @prop({ required: true })
  public uuid!: string;

  @prop({ required: false })
  public swarmBountyId?: string;

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

  @prop({ type: () => [String], default: [] })
  public dependencyTasks!: string[];

  @prop({ required: false })
  public assignees?: AssignedInfo[];

  @prop({ enum: TodoStatus, default: TodoStatus.INITIALIZED, required: true })
  public status!: TodoStatus;
}

const TodoModel = getModelForClass(Todo);
export { Todo, TodoModel, TodoStatus };
