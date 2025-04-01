  import { defaultBountyMarkdownFile } from "../../config/constant";
import  SwarmBountyModel  from "../../models/SwarmBounties";
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
     console.log('Fetching markdown file from:', defaultBountyMarkdownFile);
     const bountyMarkdownFile = await fetch(defaultBountyMarkdownFile);
     const bountyMarkdownFileText = await bountyMarkdownFile.text();
     
     console.log('Raw markdown content:', bountyMarkdownFileText);
     
     const bountyMarkdownFileLines = bountyMarkdownFileText.split("\n");
     console.log('Number of lines:', bountyMarkdownFileLines.length);
     
     const issues: BountyIssue[] = [];
     let isTableStarted = false;
     
     for (const line of bountyMarkdownFileLines) {
       // Skip empty lines
       if (line.trim() === '') {
         console.log('Skipping empty line');
         continue;
       }
       
       console.log('Processing line:', line);
       
       // Skip the title line starting with #
       if (line.startsWith('#')) {
         console.log('Found title line:', line);
         continue;
       }
       
       // Skip the header and separator lines
       if (line.startsWith('|') && line.includes('GitHub URL')) {
         console.log('Found header line');
         continue;
       }
       if (line.startsWith('|') && line.includes('-----')) {
         console.log('Found separator line');
         continue;
       }
       
       // Process table rows
       if (line.startsWith('|')) {
         isTableStarted = true;
         // Remove first and last | and split by |
         const cells = line.slice(1, -1).split('|').map(cell => cell.trim());
         console.log('Parsed cells:', cells);
         
         // Extract GitHub URL and name from markdown link format [name](url)
         const githubUrlMatch = cells[0].match(/\[(.*?)\]\((.*?)\)/);
         console.log('GitHub URL match:', githubUrlMatch);
         
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
         
         console.log('Created issue object:', issue);
         issues.push(issue);
       }
     }
     // Filter all issues with status "Initialized" && Bounty Task is Document & Summarize
     console.log('Final parsed issues number:', issues.length);
     return issues
   } catch (error) {
     console.error('Error processing markdown:', error);
     throw error;
   }
}


export async function getInitializedDocumentSummarizeIssues(issues: BountyIssue[]) {
  return issues.filter(issue => issue.status === "Initialized" && issue.bountyTask === "Document & Summarize");
}

export async function getInitializedDocumentSummarizeIssuesThroughMongoDB() {
  const issues = await SwarmBountyModel.find({ status: "loading", swarmType: "document-summarizer" });
  return issues;
}


