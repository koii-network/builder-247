import * as fzstd from 'fzstd';

export async function decodeZstd(base64ZstdData: string): Promise<Buffer> {
  const compressedData = Buffer.from(base64ZstdData, 'base64');
  const decompressedData = await fzstd.decompress(compressedData);
  return Buffer.from(decompressedData);
}
