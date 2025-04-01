import { Schema } from 'mongoose';
import { prometheusDB } from '../services/database/database';

export enum SwarmBountyStatus {
  COMPLETED = "completed",
  FAILED = "failed",
  LOADING = "loading"
}

const SwarmBountySchema = new Schema(
  {
    status: {
      type: String,
      enum: Object.values(SwarmBountyStatus),
      default: SwarmBountyStatus.LOADING,
    },
    email: {
      type: String,
      match: [/^\S+@\S+\.\S+$/, 'Please enter a valid email address'],
    },
    githubUrl: {
      type: String,
      required: [true, 'GitHub URL is required'],
      match: [
        /^https:\/\/github\.com\/.+/,
        'Must be a GitHub URL (https://github.com/...)',
      ],
    },
    projectName: {
      type: String,
    },
    description: {
      type: String,
    },
    bountyAmount: {
      type: Number,
      required: [true, 'Bounty amount is required'],
      min: [0.000001, 'Bounty amount must be greater than 0'],
    },
    isAutoIntegrationKit: {
      type: Boolean,
      default: false,
    },
    swarmType: {
      type: String,
      required: [true, 'Swarm type is required'],
      enum: ['document-summarizer', 'find-bugs', 'build-feature'],
    },
    bountyType: {
      type: String,
      required: [true, 'Bounty type is required'],
      enum: ['usdc', 'weth', 'usd', 'koii', 'kpl'],
    },
    walletAddress: {
      type: String,
      required: [true, 'Wallet address is required'],
    },
    txHash: {
      type: String,
      required: [true, 'Transaction hash is required'],
    },
  },
  {
    timestamps: true,
    collection: 'swarmbounties'
  }
);

// Check if the model is already defined to prevent overwriting during hot reloads
const SwarmBounty = prometheusDB.models.SwarmBounty || prometheusDB.model('SwarmBounty', SwarmBountySchema);

export default SwarmBounty; 