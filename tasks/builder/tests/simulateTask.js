import { taskRunner } from '@_koii/task-manager';
import { bootstrap } from '@_koii/orca-node';
import '../src/index.js';
import { namespaceWrapper } from '@_koii/namespace-wrapper';
import child_process from 'child_process';

const numRounds = process.argv[2] || 1;
const roundDelay = process.argv[3] || 5000;
const functionDelay = process.argv[4] || 1000;

let TASK_TIMES = [];
let SUBMISSION_TIMES = [];
let AUDIT_TIMES = [];

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
await namespaceWrapper.stakeOnChain();
async function executeTasks() {
  const podStopCommand = `podman pod stop undefined`;
  const podRmCommand = `podman pod rm undefined`;
  try {
    execSync(podStopCommand);
    execSync(podRmCommand);
  } catch (error) {
    console.error(error.stderr);
  }
  const orcaInstance = await bootstrap();
  orcaInstance.setErrorHandler(msg => console.error('ORCA: ', msg));
  orcaInstance.setWarnHandler(msg => console.warn('ORCA: ', msg));
  orcaInstance.setLogHandler(msg => console.log('ORCA: ', msg));
  for (let round = 0; round < numRounds; round++) {
    const taskStartTime = Date.now();
    await taskRunner.task(round);
    const taskEndTime = Date.now();
    TASK_TIMES.push(taskEndTime - taskStartTime);
    await sleep(functionDelay);

    const taskSubmissionStartTime = Date.now();
    await taskRunner.submitTask(round);
    const taskSubmissionEndTime = Date.now();
    SUBMISSION_TIMES.push(taskSubmissionEndTime - taskSubmissionStartTime);
    await sleep(functionDelay);

    const auditStartTime = Date.now();
    await taskRunner.auditTask(round);
    const auditEndTime = Date.now();
    AUDIT_TIMES.push(auditEndTime - auditStartTime);
    await sleep(functionDelay);

    await taskRunner.selectAndGenerateDistributionList(round);
    await sleep(functionDelay);

    await taskRunner.auditDistribution(round);

    if (round < numRounds - 1) {
      await sleep(roundDelay);
    }
  }
  console.log('Deleting pod...');
  deletePod();
  console.log('TIME METRICS BELOW');
  function metrics(name, times) {
    const average = arr => arr.reduce((a, b) => a + b, 0) / arr.length;
    const formatTime = ms => (ms / 1000).toFixed(4);
    const formatSlot = ms => Math.ceil(ms / 408);
    const min = Math.min(...times);
    const max = Math.max(...times);
    const avg = average(times);
    const timeMin = formatTime(min);
    const timeMax = formatTime(max);
    const timeAvg = formatTime(avg);
    const slotMin = formatSlot(min);
    const slotMax = formatSlot(max);
    const slotAvg = formatSlot(avg);

    return {
      Metric: `SIMULATED ${name} WINDOW`,
      'Avg Time (s)': timeAvg,
      'Avg Slots': slotAvg,
      'Min Time (s)': timeMin,
      'Min Slots': slotMin,
      'Max Time (s)': timeMax,
      'Max Slots': slotMax,
    };
  }
  const timeMetrics = metrics('TASK', TASK_TIMES);
  const submissionMetrics = metrics('SUBMISSION', SUBMISSION_TIMES);
  const auditMetrics = metrics('AUDIT', AUDIT_TIMES);
  console.table([timeMetrics, submissionMetrics, auditMetrics]);

  console.log('All tasks executed. Test completed.');
  process.exit(0);
}
setTimeout(executeTasks, 1500);

function deletePod() {
  function execSync(cmdstr) {
    try {
      child_process.execSync(cmdstr);
    } catch (error) {
      console.error(error);
    }
  }
  const podStopCommand = `podman pod stop undefined`;
  const podRmCommand = `podman pod rm undefined`;
  try {
    execSync(podStopCommand);
    execSync(podRmCommand);
  } catch (error) {
    console.error(error.stderr);
  }
}
