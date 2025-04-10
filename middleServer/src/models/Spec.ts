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

enum SpecStatus {

  INITIALIZED = "initialized", 

  IN_PROGRESS = "in_progress", 
  DONE = "done",
  FAILED = "failed",
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
class Spec {
  @prop({ required: true })
  public title!: string;

  @prop({ required: true })
  public description!: string;

  @prop({ required: true })
  public repoOwner!: string;

  @prop({ required: true })
  public repoName!: string;

  @prop({ required: true })
  public swarmBountyId!: string;

  @prop({ required: false })
  public taskId!: string;

  @prop({ required: false })
  public roundNumber!: number;

  @prop({ type: () => [AssignedInfo], default: [] })
  public assignedTo!: AssignedInfo[];

  @prop({
    enum: SpecStatus,
    default: SpecStatus.INITIALIZED,
    required: true,
  })
  public status!: SpecStatus;
}

const SpecModel = getModelForClass(Spec);
export { Spec, SpecModel, SpecStatus, AssignedInfo };

