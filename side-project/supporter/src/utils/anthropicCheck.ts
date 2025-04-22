export function isValidAnthropicApiKey(key: string) {
    const regex = /^sk-ant-[a-zA-Z0-9_-]{32,}$/;
    return regex.test(key);
}

export async function checkAnthropicAPIKey(apiKey: string) {
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
      'content-type': 'application/json',
    },
    body: JSON.stringify({
      model: 'claude-3-opus-20240229', // or a cheaper model
      max_tokens: 1, // minimal usage
      messages: [{ role: 'user', content: 'Hi' }],
    }),
  });

  if (response.status === 200) {
    console.log('✅ API key is valid and has credit.');
    return true;
  } else {
    const data = await response.json().catch(() => ({}));
    if (response.status === 401) {
      console.log('❌ Invalid API key.');
    } else if (response.status === 403 && data.error?.message?.includes('billing')) {
      console.log('❌ API key has no credit or is not authorized.');
    } else {
      console.log('⚠️ Unexpected error:', data);
    }
    return false;
  }
}

