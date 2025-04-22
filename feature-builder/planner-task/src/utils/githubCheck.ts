export async function checkGitHub(username: string, token: string) {
    // 1. Check username
    const userRes = await fetch(`https://api.github.com/users/${username}`);
    const isUsernameValid = userRes.status === 200;
  
    // 2. Check token
    const tokenRes = await fetch('https://api.github.com/user', {
      headers: {
        Authorization: `token ${token}`,
      },
    });
    const isTokenValid = tokenRes.status === 200;
    const isIdentityValid = await checkGitHubIdentity(username, token);
    return isIdentityValid&&isUsernameValid&&isTokenValid
}

async function checkGitHubIdentity(username: string, token: string) {
    const res = await fetch('https://api.github.com/user', {
      headers: {
        Authorization: `token ${token}`,
        Accept: 'application/vnd.github.v3+json',
      },
    });
  
    if (res.status !== 200) {
      return false
    }
  
    const data = await res.json();
  
    if (data.login.toLowerCase() !== username.toLowerCase()) {
      return false
    }
  
    return true
}