import { prop, getModelForClass, modelOptions, Severity } from "@typegoose/typegoose";

@modelOptions({
  schemaOptions: {
    timestamps: true,
  },
  options: {
    allowMixed: Severity.ALLOW,
  },
})
class SystemPrompt {
  @prop({ required: true, unique: true })
  public taskId!: string;

  @prop({ required: true })
  public prompt!: string;
}

const SystemPromptModel = getModelForClass(SystemPrompt);
export { SystemPrompt, SystemPromptModel };
