import { starRepo, createIssue, checkStarred, followUser, checkFollowed } from './gitHub';

async function main() {
  try {
    // Test starRepo
    const starResult = await starRepo("somali0128", "prometheus-swarm-bounties");
    console.log('Star repo result:', starResult);

    // Test checkStarred
    const isStarred = await checkStarred("somali0128", "prometheus-swarm-bounties");
    console.log('Is starred:', isStarred);

    // Test followUser
    const followResult = await followUser("somali0128");
    console.log('Follow user result:', followResult);

    // Test checkFollowed
    const isFollowing = await checkFollowed("somali0128");
    console.log('Is following:', isFollowing);

    // Test createIssue
    const issueResult = await createIssue(
      "somali0128",
      "prometheus-swarm-bounties",
      "Test Issue",
      "This is a test issue created via API"
    );
    console.log('Create issue result:', issueResult);
  } catch (error) {
    console.error('Error:', error);
  }
}

main();
