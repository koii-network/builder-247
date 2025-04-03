import { KoiiStorageClient } from '@_koii/storage-task-sdk';

export async function getFile(cid: string, filename: string = 'submission.json'): Promise<string> {
    const storageClient = KoiiStorageClient.getInstance({});
    const fileBlob = await storageClient.getFile(cid, filename);
    return await fileBlob.text();
  }