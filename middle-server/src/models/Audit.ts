import { prop, getModelForClass, modelOptions, Severity } from "@typegoose/typegoose";

enum AuditStatus {
  PENDING = "pending",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  FAILED = "failed",
}

@modelOptions({
  schemaOptions: {
    timestamps: true,
  },
  options: {
    allowMixed: Severity.ALLOW,
  },
})
class Audit {
  @prop({ required: true })
  public taskId!: string;

  @prop({ required: true })
  public roundNumber!: number;

  @prop({ enum: AuditStatus, default: AuditStatus.PENDING })
  public status!: AuditStatus;

  @prop({ default: 0 })
  public todosProcessed!: number;

  @prop({ default: 0 })
  public issuesProcessed!: number;

  @prop({ default: null })
  public error?: string;
}

const AuditModel = getModelForClass(Audit);
export { Audit, AuditModel, AuditStatus };
