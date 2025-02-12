/** EXAMPLE PODSPEC
 *
 * NOTE: The spacing is critical in YAML files
 * use template literal (``) to preserve whitespace

Do not change containers > name. You must specify your container image here.

*/

import { TASK_ID } from "@_koii/namespace-wrapper";
const podId = TASK_ID;
import "dotenv/config";

const podSpec = `apiVersion: v1
kind: Pod
metadata:
  name: 247-builder-test
spec:
  containers:
    - name: user-${podId}
      image: docker.io/labrocadabro/builder247:0.3
      env:
      - name: GITHUB_TOKEN
        value: "${process.env.GITHUB_TOKEN}"
      - name: GITHUB_USERNAME
        value: "${process.env.GITHUB_USERNAME}"
      - name: CLAUDE_API_KEY
        value: "${process.env.CLAUDE_API_KEY}"
`;

// const podSpec = null;

export const config = {
  // location of your docker image
  imageURL: "docker.io/labrocadabro/builder247:0.3",
  // if you are using a podSpec, edit it in podSpec.js
  customPodSpec: podSpec,
  // SSL
  rootCA: null,
};
