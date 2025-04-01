import { prop, getModelForClass, modelOptions, Severity } from "@typegoose/typegoose";
import { builder247DB } from "../utils/database";

@modelOptions({ 
  schemaOptions: { collection: 'summarizer_records' },
  existingConnection: builder247DB
})
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