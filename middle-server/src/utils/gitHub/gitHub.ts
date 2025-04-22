export async function createFork(repoUrl: string) {
    const { Octokit } = await import('@octokit/rest');
    const octokit = new Octokit({
        auth: process.env.GITHUB_TOKEN,
    });

    const repo = repoUrl.split("/").pop();
    const owner = repoUrl.split("/")[3];

    if (!owner || !repo) {
        throw new Error("Invalid repository URL");
    }

    const fork = await octokit.rest.repos.createFork({
        owner,
        repo,
    });

    return fork.data.html_url;
}


