export interface BaseSignaturePayload {
  taskId: string;
  roundNumber: number;
  stakingKey: string;
  action: string;
}

export interface FetchSignaturePayload extends BaseSignaturePayload {
  githubUsername: string;
}

export interface AddSignaturePayload extends BaseSignaturePayload {
  prUrl: string;
  pubKey: string;
}

export interface AddAggregatorPayload extends BaseSignaturePayload {
  githubUsername: string;
  issueUuid: string;
  pubKey: string;
}

export type SignaturePayload = FetchSignaturePayload | AddSignaturePayload | AddAggregatorPayload; 