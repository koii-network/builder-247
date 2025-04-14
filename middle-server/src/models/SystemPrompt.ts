import { prop, getModelForClass, modelOptions, Severity } from "@typegoose/typegoose";
import { builder247DB } from "../services/database/database";
@modelOptions({
  schemaOptions: {
    timestamps: true,
  },
  options: {
    allowMixed: Severity.ALLOW,
  },
  existingConnection: builder247DB,
})
class SystemPrompt {
  @prop({ required: true, unique: true })
  public taskId!: string;

  @prop({ required: true })
  public prompt!: string;
}

const SystemPromptModel = getModelForClass(SystemPrompt);
export { SystemPrompt, SystemPromptModel };
