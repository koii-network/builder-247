import { getOrcaClient } from "@_koii/task-manager/extensions";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import "dotenv/config";
import { getRandomNodes } from "../utils/leader";
import { getExistingIssues } from "../utils/existingIssues";
import { status, middleServerUrl } from "../utils/constant";
import dotenv from "dotenv";
import { checkAnthropicAPIKey, isValidAnthropicApiKey } from "../utils/anthropicCheck";
import { checkGitHub } from "../utils/githubCheck";
import { LogLevel } from "@_koii/namespace-wrapper/dist/types";
import { actionMessage } from "../utils/constant";
import { errorMessage } from "../utils/constant";
import { storeFile } from "../utils/ipfs";
dotenv.config();


export async function task(roundNumber: number): Promise<void> {
  /**
   * Run your task and store the proofs to be submitted for auditing
   * It is expected you will store the proofs in your container
   * The submission of the proofs is done in the submission function
   */
  // FORCE TO PAUSE 30 SECONDS
// No submission on Round 0 so no need to trigger fetch audit result before round 3
// Changed from 3 to 4 to have more time
  if (roundNumber >= 4) {
    const triggerFetchAuditResult = await fetch(`${middleServerUrl}/api/planner/trigger-fetch-audit-result`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ taskId: TASK_ID, round: roundNumber - 4 })
    });
    console.log(`[TASK] Trigger fetch audit result for round ${roundNumber - 3}. Result is ${triggerFetchAuditResult.status}.`);
  }
  console.log(`[TASK] EXECUTE TASK FOR ROUND ${roundNumber}`);
  try {
    const orcaClient = await getOrcaClient();
    // check if the env variable is valid
    if (!process.env.ANTHROPIC_API_KEY) {
      await namespaceWrapper.logMessage(LogLevel.Error, errorMessage.ANTHROPIC_API_KEY_INVALID, actionMessage.ANTHROPIC_API_KEY_INVALID);
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ANTHROPIC_API_KEY_INVALID);
      return;
    }
    if (!isValidAnthropicApiKey(process.env.ANTHROPIC_API_KEY!)) {
      await namespaceWrapper.logMessage(LogLevel.Error, errorMessage.ANTHROPIC_API_KEY_INVALID, actionMessage.ANTHROPIC_API_KEY_INVALID);
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ANTHROPIC_API_KEY_INVALID);
      return;
    }
    const isAnthropicAPIKeyValid = await checkAnthropicAPIKey(process.env.ANTHROPIC_API_KEY!);
    if (!isAnthropicAPIKeyValid) {
      await namespaceWrapper.logMessage(LogLevel.Error, errorMessage.ANTHROPIC_API_KEY_NO_CREDIT, actionMessage.ANTHROPIC_API_KEY_NO_CREDIT);
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ANTHROPIC_API_KEY_NO_CREDIT);
      return;
    }
    // if (!process.env.GITHUB_USERNAME || !process.env.GITHUB_TOKEN) {
    //   await namespaceWrapper.logMessage(LogLevel.Error, errorMessage.GITHUB_CHECK_FAILED, actionMessage.GITHUB_CHECK_FAILED);
    //   await namespaceWrapper.storeSet(`result-${roundNumber}`, status.GITHUB_CHECK_FAILED);
    //   return;
    // }
    // const isGitHubValid = await checkGitHub(process.env.GITHUB_USERNAME!, process.env.GITHUB_TOKEN!);
    // if (!isGitHubValid) {
    //   await namespaceWrapper.logMessage(LogLevel.Error, errorMessage.GITHUB_CHECK_FAILED, actionMessage.GITHUB_CHECK_FAILED);
    //   await namespaceWrapper.storeSet(`result-${roundNumber}`, status.GITHUB_CHECK_FAILED);
    //   return;
    // }
    if (!orcaClient) {
      await namespaceWrapper.logMessage(LogLevel.Error, errorMessage.NO_ORCA_CLIENT, actionMessage.NO_ORCA_CLIENT);
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.NO_ORCA_CLIENT);
      return;
    }

    const stakingKeypair = await namespaceWrapper.getSubmitterAccount();
    if (!stakingKeypair) {
      throw new Error("No staking keypair found");
    }
    const stakingKey = stakingKeypair.publicKey.toBase58();
    const pubKey = await namespaceWrapper.getMainAccountPubkey();
    if (!pubKey) {
      throw new Error("No public key found");
    }


    const signature = await namespaceWrapper.payloadSigning(
      {
        taskId: TASK_ID,
        roundNumber: roundNumber,
        action: "fetch",
        githubUsername: stakingKey,
        stakingKey: stakingKey
      },
      stakingKeypair.secretKey,
    );

    // const initializedDocumentSummarizeIssues = await getInitializedDocumentSummarizeIssues(existingIssues);

    console.log(`[TASK] Making Request to Middle Server with taskId: ${TASK_ID} and round: ${roundNumber}`);
    console.log(`[TASK] request body: ${JSON.stringify({ signature: signature, stakingKey: stakingKey })}`);
    const requiredWorkResponse = await fetch(`${middleServerUrl}/api/planner/fetch-planner-todo`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ signature: signature, stakingKey: stakingKey }),
    });
    // check if the response is 200
    if (requiredWorkResponse.status !== 200) {
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.NO_ISSUES_PENDING_TO_BE_SUMMARIZED);
      return;
    }
    const requiredWorkResponseData = await requiredWorkResponse.json();
    console.log("[TASK] requiredWorkResponseData: ", requiredWorkResponseData);

    const jsonBody = {
      repoUrl: `https://github.com/${requiredWorkResponseData.data.repo_owner}/${requiredWorkResponseData.data.repo_name}`,
      issueSpec: requiredWorkResponseData.data.description
    };
    console.log("[TASK] jsonBody: ", jsonBody);
    try {
      const repoSummaryResponse = await orcaClient.podCall(`task/${roundNumber}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(jsonBody),
      });
      console.log("[TASK] repoSummaryResponse: ", repoSummaryResponse);
      /***
       * {
    "data": {
        "issues": [
            {
                "description": "Add robust input validation for the Easy Refine functionality to ensure data integrity and prevent potential errors. \n\nSpecific validation requirements:\n- Validate input parameters for type, range, and format\n- Implement error handling for invalid inputs\n- Create clear error messages for different validation scenarios\n- Ensure validation is performed before processing any refine operations\n\nAcceptance Criteria:\n- All input parameters are checked for validity before processing\n- Invalid inputs are rejected with informative error messages\n- No unhandled exceptions can occur during the input validation process\n- Unit tests cover various input validation scenarios",
                "title": "Implement Input Validation for Easy Refine Parameters",
                "uuid": "d4d9c02e-3cdb-410d-85fd-60f5c94e01d5"
            }
        ],
        "tasks": [
            [
                {
                    "acceptanceCriteria": "Create a JSON or YAML schema document detailing validation rules for each parameter\nValidation schema must cover all input parameters used in Easy Refine\nSchema must include type, range, and format constraints\n100% coverage of parameter validation rules documented",
                    "assignedTo": [],
                    "dependencyTasks": [],
                    "description": "Create a comprehensive validation schema that defines the expected types, ranges, and formats for all input parameters used in the Easy Refine functionality. This task involves:\n- Identifying all input parameters\n- Defining type constraints (e.g., string, integer, boolean)\n- Establishing valid ranges and formats\n- Documenting validation rules for each parameter",
                    "issueUuid": "d4d9c02e-3cdb-410d-85fd-60f5c94e01d5",
                    "repoName": "NSOutage",
                    "repoOwner": "HermanL02",
                    "status": "initialized",
                    "title": "Design Input Validation Schema for Easy Refine Parameters",
                    "uuid": "e0291bd7-f84c-4466-9e47-63db4f78432e"
                },
                {
                    "acceptanceCriteria": "Develop a type validation function that returns clear error messages\nImplement type validation for all input parameters\nEnsure 100% branch coverage for type validation logic\nCreate unit tests covering valid and invalid input type scenarios",
                    "assignedTo": [],
                    "dependencyTasks": [
                        "e0291bd7-f84c-4466-9e47-63db4f78432e",
                        "773ee93c-81ad-4dbd-ad4a-cb5ea5ac8f8d"
                    ],
                    "description": "Develop a robust middleware or validation function that checks input parameter types before processing any Easy Refine operations. This task includes:\n- Creating type checking logic for each parameter\n- Implementing type conversion where appropriate\n- Handling type mismatch scenarios\n- Generating clear error messages for type validation failures",
                    "issueUuid": "d4d9c02e-3cdb-410d-85fd-60f5c94e01d5",
                    "repoName": "NSOutage",
                    "repoOwner": "HermanL02",
                    "status": "initialized",
                    "title": "Implement Input Type Validation Middleware",
                    "uuid": "8e9fdebb-47de-459e-86de-6d1077442766"
                },
                {
                    "acceptanceCriteria": "Implement validation functions for numeric range constraints\nCreate regex-based format validation for string inputs\nGenerate descriptive error messages for range and format violations\nAchieve 90% test coverage for range and format validation logic",
                    "assignedTo": [],
                    "dependencyTasks": [
                        "e0291bd7-f84c-4466-9e47-63db4f78432e",
                        "8e9fdebb-47de-459e-86de-6d1077442766"
                    ],
                    "description": "Implement detailed validation for input parameter ranges and formats. This includes:\n- Creating validation functions for numeric ranges\n- Implementing regex or pattern matching for string formats\n- Handling date/time format validations\n- Generating specific error messages for range and format violations",
                    "issueUuid": "d4d9c02e-3cdb-410d-85fd-60f5c94e01d5",
                    "repoName": "NSOutage",
                    "repoOwner": "HermanL02",
                    "status": "initialized",
                    "title": "Develop Range and Format Validation Logic",
                    "uuid": "773ee93c-81ad-4dbd-ad4a-cb5ea5ac8f8d"
                },
                {
                    "acceptanceCriteria": "Create a standardized error response format with detailed error information\nMap validation errors to appropriate HTTP status codes (e.g., 400 Bad Request)\nImplement error logging for all validation failures\nEnsure 100% exception handling coverage\nVerify no unhandled exceptions can occur during input validation",
                    "assignedTo": [],
                    "dependencyTasks": [
                        "e0291bd7-f84c-4466-9e47-63db4f78432e",
                        "8e9fdebb-47de-459e-86de-6d1077442766",
                        "773ee93c-81ad-4dbd-ad4a-cb5ea5ac8f8d"
                    ],
                    "description": "Develop a structured error handling mechanism for input validation failures. This task involves:\n- Creating a custom error response structure\n- Mapping validation errors to appropriate HTTP status codes\n- Implementing detailed error logging\n- Ensuring no unhandled exceptions occur during validation",
                    "issueUuid": "d4d9c02e-3cdb-410d-85fd-60f5c94e01d5",
                    "repoName": "NSOutage",
                    "repoOwner": "HermanL02",
                    "status": "initialized",
                    "title": "Implement Comprehensive Error Handling for Input Validation",
                    "uuid": "6fb33c70-a9d5-4a23-8354-51b3113079f2"
                },
                {
                    "acceptanceCriteria": "Develop unit tests covering 100% of validation logic\nCreate integration tests simulating various input scenarios\nTest all edge cases and boundary conditions\nVerify error messages are clear and informative\nAchieve 95% overall test coverage for input validation system",
                    "assignedTo": [],
                    "dependencyTasks": [
                        "e0291bd7-f84c-4466-9e47-63db4f78432e",
                        "8e9fdebb-47de-459e-86de-6d1077442766",
                        "773ee93c-81ad-4dbd-ad4a-cb5ea5ac8f8d",
                        "6fb33c70-a9d5-4a23-8354-51b3113079f2"
                    ],
                    "description": "Develop a comprehensive test suite to verify the input validation implementation. This includes:\n- Writing unit tests for individual validation functions\n- Creating integration tests that validate the entire validation workflow\n- Testing edge cases and boundary conditions\n- Verifying error handling and message generation",
                    "issueUuid": "d4d9c02e-3cdb-410d-85fd-60f5c94e01d5",
                    "repoName": "NSOutage",
                    "repoOwner": "HermanL02",
                    "status": "initialized",
                    "title": "Create Unit and Integration Tests for Input Validation",
                    "uuid": "74d729e6-ff21-4ae1-8478-68c95b5f8c16"
                }
            ]
        ]
    },
    "success": true
}
       */

      const ipfs_cid = await storeFile(repoSummaryResponse.data.data);
      await namespaceWrapper.storeSet(`ipfs-cid-${roundNumber}`, ipfs_cid);
      console.log("[TASK] repoSummaryResponse.data.data ", repoSummaryResponse.data.data);
      const payload = {
        taskId: TASK_ID,
        action: "add",
        roundNumber: roundNumber,
        prUrl: ipfs_cid,
        stakingKey: stakingKey
      }
      console.log("[TASK] Signing payload: ", payload);
      if (repoSummaryResponse.status === 200) {
        try{
          const signature = await namespaceWrapper.payloadSigning(
            payload,
            stakingKeypair.secretKey,
          );
          console.log("[TASK] signature: ", signature);
          const addPrToSummarizerTodoResponse = await fetch(`${middleServerUrl}/api/planner/add-pr-to-planner-todo`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ signature: signature, stakingKey: stakingKey }),
          });
          console.log("[TASK] addPrToSummarizerTodoResponse: ", addPrToSummarizerTodoResponse);
          await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ISSUE_SUCCESSFULLY_SUMMARIZED);
        }catch(error){
          await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ISSUE_FAILED_TO_ADD_PR_TO_SUMMARIZER_TODO);
          console.error("[TASK] Error adding PR to summarizer todo:", error);
        }

      } else {
        await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ISSUE_FAILED_TO_BE_SUMMARIZED);
      }
    } catch (error) {
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ISSUE_FAILED_TO_BE_SUMMARIZED);

      // try{
      //   const slackResponse = await fetch('https://hooks.slack.com/services', {
      //     method: "POST",
      //     headers: {
      //       "Content-Type": "application/json",
      //     },
      //     body: JSON.stringify({
      //       text: `[TASK] Error summarizing issue:\n ${JSON.stringify(error)}`
      //     }),
      //   });
      //   console.log("[TASK] slackResponse: ", slackResponse);
      // }catch(error){
      //   console.error("[TASK] Error posting to slack:", error);
      // }
      console.error("[TASK] EXECUTE TASK ERROR:", error);
    }
  } catch (error) {
    await namespaceWrapper.storeSet(`result-${roundNumber}`, status.UNKNOWN_ERROR);
    console.error("[TASK] EXECUTE TASK ERROR:", error);
  }
}
