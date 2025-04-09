// async function testSlackWebhook(){
//     const slackResponse = await fetch('https://hooks.slack.com/services/', {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json",
//     },
//     body: JSON.stringify({ 
//       text: `[TASK] Error summarizing issue:\n ${JSON.stringify({
//         status: "error",
//         data: {
//           message: "test"
//         }
//       })}`
//     }),
//   });
//   console.log("[TASK] slackResponse: ", slackResponse);
// }

// testSlackWebhook();