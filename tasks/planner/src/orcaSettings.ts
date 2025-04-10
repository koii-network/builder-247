import { TASK_ID, namespaceWrapper } from "@_koii/namespace-wrapper";
import "dotenv/config";

const imageUrl = "docker.io/hermanyiqunliang/planner-agent:0.2";

async function createPodSpec(): Promise<string> {
  const basePath = await namespaceWrapper.getBasePath();

  const podSpec = `apiVersion: v1
kind: Pod
metadata:
  name: 247-builder-test
spec:
  containers:
    - name: user-${TASK_ID}
      image: ${imageUrl}
      env:
      - name: GITHUB_TOKEN
        value: "${process.env.GITHUB_TOKEN}"
      - name: GITHUB_USERNAME
        value: "${process.env.GITHUB_USERNAME}"
      - name: ANTHROPIC_API_KEY
        value: "${process.env.ANTHROPIC_API_KEY}"
      volumeMounts:
        - name: builder-data
          mountPath: /data
  volumes:
    - name: builder-data
      hostPath:
        path: ${basePath}/orca/data
        type: DirectoryOrCreate
`;
  return podSpec;
}

export async function getConfig(): Promise<{
  imageURL: string;
  customPodSpec: string;
  rootCA: string | null;
}> {
  return {
    imageURL: imageUrl,
    customPodSpec: await createPodSpec(),
    rootCA: null,
  };
}
