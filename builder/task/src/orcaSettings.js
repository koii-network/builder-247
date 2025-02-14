import { TASK_ID, namespaceWrapper } from "@_koii/namespace-wrapper";
const podId = TASK_ID;
import "dotenv/config";

async function createPodSpec() {
  const basePath = await namespaceWrapper.getBasePath();

  const podSpec = `apiVersion: v1
kind: Pod
metadata:
  name: 247-builder-test
spec:
  containers:
    - name: user-${podId}
      image: docker.io/labrocadabro/builder247:0.5
      env:
      - name: GITHUB_TOKEN
        value: "${process.env.GITHUB_TOKEN}"
      - name: GITHUB_USERNAME
        value: "${process.env.GITHUB_USERNAME}"
      - name: CLAUDE_API_KEY
        value: "${process.env.CLAUDE_API_KEY}"
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

export async function getConfig() {
  return {
    imageURL: "docker.io/labrocadabro/builder247:0.5",
    customPodSpec: await createPodSpec(),
    rootCA: null,
  };
}
