import { defaultBountyMarkdownFile } from "./constant";

interface BountyIssue {
  githubUrl: string;
  projectName: string;
  bountyTask: string;
  description: string;
  bountyAmount: string;
  bountyType: string;
  transactionHash: string;
  status: string;
}

export async function getExistingIssues(): Promise<BountyIssue[]> {
   try {
     // read from the bounty markdown file
    //  console.log('Fetching markdown file from:', defaultBountyMarkdownFile);
     const bountyMarkdownFile = await fetch(defaultBountyMarkdownFile);
     const bountyMarkdownFileText = await bountyMarkdownFile.text();
     
    //  console.log('Raw markdown content:', bountyMarkdownFileText);
     
     const bountyMarkdownFileLines = bountyMarkdownFileText.split("\n");
    //  console.log('Number of lines:', bountyMarkdownFileLines.length);
     
     const issues: BountyIssue[] = [];
     let isTableStarted = false;
     
     for (const line of bountyMarkdownFileLines) {
       // Skip empty lines
       if (line.trim() === '') {
        //  console.log('Skipping empty line');
         continue;
       }
       
      //  console.log('Processing line:', line);
       
       // Skip the title line starting with #
       if (line.startsWith('#')) {
        //  console.log('Found title line:', line);
         continue;
       }
       
       // Skip the header and separator lines
       if (line.startsWith('|') && line.includes('GitHub URL')) {
         //console.log('Found header line');
         continue;
       }
       if (line.startsWith('|') && line.includes('-----')) {
        //  console.log('Found separator line');
         continue;
       }
       
       // Process table rows
       if (line.startsWith('|')) {
         isTableStarted = true;
         // Remove first and last | and split by |
         const cells = line.slice(1, -1).split('|').map(cell => cell.trim());
        //  console.log('Parsed cells:', cells);
         
         // Extract GitHub URL and name from markdown link format [name](url)
         const githubUrlMatch = cells[0].match(/\[(.*?)\]\((.*?)\)/);
        //  console.log('GitHub URL match:', githubUrlMatch);
         
         const projectName = githubUrlMatch ? githubUrlMatch[1] : '';
         const githubUrl = githubUrlMatch ? githubUrlMatch[2] : '';
         
         const issue: BountyIssue = {
           githubUrl,
           projectName,
           bountyTask: cells[1],
           description: cells[3],
           bountyAmount: cells[4],
           bountyType: cells[5],
           transactionHash: cells[6],
           status: cells[7]
         };
         
        //  console.log('Created issue object:', issue);
         issues.push(issue);
       }
     }
     // Filter all issues with status "Initialized" && Bounty Task is Document & Summarize
     console.log('Final parsed issues number:', issues.length);
     return issues
   } catch (error) {
    //  console.error('Error processing markdown:', error);
     throw error;
   }
}


export async function getInitializedDocumentSummarizeIssues(issues: BountyIssue[]) {
  
  return issues.filter(issue => issue.status === "Initialized" && issue.bountyTask === "Document & Summarize");
}


// async function main(){
//   const existingIssues = await getExistingIssues();
//   const transactionHashs = [
//     "51680569890c40efa0f1f891044db219",
//     "21a7021da88a4092af014702da7638cb",
//     "befcf8d281074e3e934d8947c02ecb6f",
//     "a1db701bbda24a45b573e58840d9b31c",
//     "4ab503566a1142b1a3a9b406849839c9",
//     "7f6fb74e4b6a41b0af805ca3f6c9ea15",
//     "878af0d284c7460394b6d6e1090119be",
//     "64d90b6f891d4ea385c8f6ad81808103",
//     "6f7522b2e2374d4ca4f92bcf1f694bec",
//     "e85201ae9ed9417e8c56216bb44cd78b",
//     "d2ca259ef6ce4129a786677d919aad24",
//     "6ce684318aab4356b76ba64e87b31be7",
//     "d94d07647b1b42819d9bf629f5624ae1",
//     "60aa8f04dd314c14b30e5ac2957bd9f8",
//     "b7e21455e41b4626b5015b7bf39ff190",
//     "5e7109ed4dd94373958eda2416337ad3",
//     "2d647d3ab2c5465890939315ada47fd7",
//     "51ade1ba2f6341e99aa6ec56b1a00f27",
//     "a74f5e80238a4582aa444c18e9d5d66f",
//     "8390a3143a8445f196a124605e524f3d",
//     "26b712f341ca457d86db67ecd841c438",
//     "0ec98ba1e7174eef87772df8356bab0d",
//     "2737c33bff8c4490b7e5f53a5f5da580",
//     "e5b9b714d5694680a56cfa77361f3477",
//     "afb1bbbf1c074d28bef5fa216008cd6b",
//     "b40da8c53a644a6e898e3314e08c10ea",
//     "6a2f743c0497427ea4cd3cadb785b166",
//     "ce390111854b4a4b980b5e1e3f7c2f0e",
//     "c1b54e7a8dfd40be873051dd64bae5c4",
//     "7dcda8e5969c45e08f9a8887d8c39d10",
//     "fc11382529644d55b95fc2264e40436f",
//     "7c145db039b64edba719e81dd398b37e",
//     "c92b4920b25540a692c3b8e12215f0e0",
//     "cebbf4e2310d4a11ac44321823ddb373",
//     "5ae707005d0e413cb9feb9bdadc1e987",
//     "d28f92643c2548338d3e49144bc66afc",
//     "bd18484224c24fc786a5171e9d06cd50",
//     "f0605ea0f9524572bbe5bf4e72597476",
//     "62e6303c57334f72ada393bfa9e7aacc",
//     "f4ee9168804c4b01932ac76cc32d1f13",
//     "d4a95e2d35db47d28a208309019b1925",
//     "014425adc1b8447ab34d7d8104e91cf0"
//   ]
//   const initializedDocumentSummarizeIssues = existingIssues.filter((issue) => transactionHashs.includes(issue.transactionHash));
//   if (initializedDocumentSummarizeIssues.length == 0) {
//     console.log("No issues pending to be summarized");
//     return;
//   } 
//   console.log("Initialized Document & Summarize issues number:", initializedDocumentSummarizeIssues.length);
// }
// async function main() {
//    try {
//      const existingIssues = await getInitializedDocumentSummarizeIssues();
//      console.log('Initialized Document & Summarize issues number:', existingIssues.length);
//    } catch (error) {
//      console.error('Error in main:', error);
//    }
// }

// main();