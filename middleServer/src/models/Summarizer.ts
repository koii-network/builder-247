import { prop, getModelForClass, modelOptions, Severity } from "@typegoose/typegoose";



class SummarizerRecord {
  @prop({ required: true })
  public taskID!: string;
  @prop({ required: true })
  public roundNumber!: number;
  @prop({ required: true })
  public transactionHashs!: string[];
  
}

const SummarizerRecordModel = getModelForClass(SummarizerRecord);
export { SummarizerRecord, SummarizerRecordModel };
