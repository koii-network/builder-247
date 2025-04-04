export function isValidAnthropicApiKey(key: string) {
    const regex = /^sk-ant-[a-zA-Z0-9_-]{32,}$/;
    return regex.test(key);
}
  
// function test() {
//     const key = "sk-ant-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"; // Replace with your API key
//     console.log(isValidAnthropicApiKey(key));
// }

// test(); 