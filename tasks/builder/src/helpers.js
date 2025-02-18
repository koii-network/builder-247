import { namespaceWrapper } from '@_koii/namespace-wrapper';
import { KoiiStorageClient } from '@_koii/storage-task-sdk';
import fs from 'fs';

export async function storeFile(data, filename = 'submission.json') {
  // Create a new instance of the Koii Storage Client
  const client = KoiiStorageClient.getInstance();
  const basePath = await namespaceWrapper.getBasePath();
  try {
    // Write the data to a temp file
    fs.writeFileSync(
      `${basePath}/${filename}`,
      typeof data === 'string' ? data : JSON.stringify(data),
    );

    // Get the user staking account, to be used for signing the upload request
    const userStaking = await namespaceWrapper.getSubmitterAccount();

    // Upload the file to IPFS and get the CID
    const { cid } = await client.uploadFile(
      `${basePath}/${filename}`,
      userStaking,
    );
    return cid;
  } catch (error) {
    throw error;
  } finally {
    // Delete the temp file
    fs.unlinkSync(`${basePath}/${filename}`);
  }
}

export async function getFile(cid, filename = 'submission.json') {
  const storageClient = KoiiStorageClient.getInstance();
  const fileBlob = await storageClient.getFile(cid, filename);
  return await fileBlob.text();
}
