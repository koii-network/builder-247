export async function checkGitHub(token: string) {
    const tokenRes = await fetch('https://api.github.com/user', {
      headers: {
        Authorization: `token ${token}`,
      },
    });
    const isTokenValid = tokenRes.status === 200;
    return isTokenValid
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