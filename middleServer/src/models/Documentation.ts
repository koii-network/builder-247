import { prop, getModelForClass, modelOptions, Severity } from "@typegoose/typegoose";
import { builder247DB } from "../services/database/database";
class AssignedInfo {
  @prop({ required: true })
  public stakingKey!: string;

  @prop({ required: true })
  public taskId!: string;

  @prop({ required: true })
  public roundNumber!: number;

  @prop({ required: false })
  public prUrl?: string;

  @prop({ required: false })
  public auditResult?: boolean;
}

enum DocumentationStatus {
  // Means not assigned to any node
  // This  can also be used when a node is audited as false, so we can reassign it to another node
  INITIALIZED = "initialized", 
  // Means is assigned to a node, not completed
  // This can be used when the node does not complete a task, so we can reassign it to another node
  IN_PROGRESS = "in_progress", 
  DONE = "done", // Means a PR is audited and waiting for merge
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
class Documentation {
  @prop({ required: true })
  public repoOwner!: string;

  @prop({ required: true })
  public repoName!: string;

  @prop({ required: false })
  public swarmBountyId?: string;
  
  @prop({ required: false })
  public taskId!: string;

  @prop({ required: false })
  public roundNumber!: number;

  @prop({ type: () => [AssignedInfo], default: [] })
  public assignedTo!: AssignedInfo[];

  @prop({
    enum: DocumentationStatus,
    default: DocumentationStatus.INITIALIZED,
    required: true,
  })
  public status!: DocumentationStatus;
}

const DocumentationModel = getModelForClass(Documentation);
export { Documentation, DocumentationModel, DocumentationStatus, AssignedInfo };

