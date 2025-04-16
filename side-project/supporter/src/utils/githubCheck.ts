export async function checkGitHub(token: string) {
    const tokenRes = await fetch('https://api.github.com/user', {
      headers: {
        Authorization: `token ${token}`,
      },
    });
    const isTokenValid = tokenRes.status === 200;
    return isTokenValid
}
