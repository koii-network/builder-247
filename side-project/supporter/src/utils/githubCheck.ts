export async function checkGitHub(token: string) {
    const tokenRes = await fetch('https://api.github.com/user', {
      headers: {
        Authorization: `token ${token}`,
      },
    });
    const isTokenValid = tokenRes.status >= 200 && tokenRes.status < 300;
    console.log("[UTILS] Token valid:", tokenRes);
    return isTokenValid
}
