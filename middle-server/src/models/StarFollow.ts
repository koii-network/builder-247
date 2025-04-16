import { prop, getModelForClass, modelOptions, Severity } from "@typegoose/typegoose";
import { builder247DB } from "../services/database/database";

@modelOptions({
  schemaOptions: {
    timestamps: true,
  },
  options: {
    allowMixed: Severity.ALLOW,
  },
  existingConnection: builder247DB
})


class StarFollow {
  @prop({ required: true })
  public gitHubId!: string;

  @prop({ required: true })
  public stakingKey!: string;
  
  // Username is changable, so we store GitHubUsername as a backup
  @prop({ required: true })
  public gitHubUsername!: string;

  @prop({ required: false })
  public taskId!: string;

  @prop({ required: false })
  public pendingRepos!: string[];

  @prop({ required: false })
  public completedRepos!: string[];
}

const StarFollowModel = getModelForClass(StarFollow);
export { StarFollow, StarFollowModel };

