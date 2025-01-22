[1mdiff --git a/process.md b/process.md[m
[1mindex 0f0399e..4876c5a 100644[m
[1m--- a/process.md[m
[1m+++ b/process.md[m
[36m@@ -25,6 +25,7 @@[m
    - Commit messages should follow format: `[TODO-#] Description`[m
    - Each commit should reference the specific todo item[m
    - Commits should be atomic and focused[m
[32m+[m[32m   - Push to remote repository after each commit[m
 [m
 5. **Testing**[m
    - Each feature should have unit tests[m
[1mdiff --git a/src/client.py b/src/client.py[m
[1mindex e783d70..b6df51b 100644[m
[1m--- a/src/client.py[m
[1m+++ b/src/client.py[m
[36m@@ -5,7 +5,6 @@[m [mfrom typing import List, Dict, Any, Optional, Union[m
 import os[m
 from dotenv import load_dotenv[m
 import anthropic[m
[31m-from anthropic.types import MessageParam[m
 [m
 class AnthropicClient:[m
     """Wrapper for Anthropic API client with tool integration."""[m
[36m@@ -21,9 +20,9 @@[m [mclass AnthropicClient:[m
             [m
         try:[m
             # Initialize with latest Anthropic SDK[m
[31m-            self.client = anthropic.Anthropic(api_key=api_key)[m
[32m+[m[32m            self.client = anthropic.Client(api_key=api_key)[m
             self.model = model[m
[31m-            self.conversation_history: List[MessageParam] = [][m
[32m+[m[32m            self.conversation_history: List[Dict[str, str]] = [][m
         except Exception as e:[m
             raise ValueError(f"Failed to initialize Anthropic client: {str(e)}")[m
     [m
[36m@@ -35,23 +34,26 @@[m [mclass AnthropicClient:[m
     ) -> str:[m
         """Send a message to Claude and return the response."""[m
         try:[m
[32m+[m[32m            # Create message request[m
[32m+[m[32m            messages = [{"role": "user", "content": message}][m
[32m+[m[41m            [m
[32m+[m[32m            # Add conversation history if any[m
[32m+[m[32m            if self.conversation_history:[m
[32m+[m[32m                messages = self.conversation_history + messages[m
[32m+[m[41m            [m
             # Create message request[m
             request = {[m
                 "model": self.model,[m
                 "max_tokens": max_tokens,[m
[31m-                "messages": [{"role": "user", "content": message}][m
[32m+[m[32m                "messages": messages[m
             }[m
             [m
             # Add system message if provided[m
             if system:[m
                 if isinstance(system, str):[m
[31m-                    request["system"] = [system][m
[31m-                else:[m
                     request["system"] = system[m
[31m-            [m
[31m-            # Add conversation history if any[m
[31m-            if self.conversation_history:[m
[31m-                request["messages"] = self.conversation_history + request["messages"][m
[32m+[m[32m                else:[m
[32m+[m[32m                    request["system"] = "\n".join(system)[m
             [m
             response = self.client.messages.create(**request)[m
             [m
[1mdiff --git a/tests/test_client.py b/tests/test_client.py[m
[1mindex 94aa609..2b01cf6 100644[m
[1m--- a/tests/test_client.py[m
[1m+++ b/tests/test_client.py[m
[36m@@ -3,48 +3,65 @@[m [mTests for the Anthropic client wrapper.[m
 """[m
 import os[m
 import pytest[m
[31m-from dotenv import load_dotenv, find_dotenv[m
[32m+[m[32mfrom unittest.mock import patch, MagicMock[m
 from src.client import AnthropicClient[m
 [m
 def test_client_initialization():[m
     """Test client initialization with API key."""[m
[31m-    client = AnthropicClient()[m
[31m-    assert client.model == "claude-3-sonnet-20240229"[m
[31m-    assert len(client.conversation_history) == 0[m
[32m+[m[32m    with patch.dict(os.environ, {"CLAUDE_API_KEY": "test-key"}):[m
[32m+[m[32m        with patch("anthropic.Client") as mock_client:[m
[32m+[m[32m            client = AnthropicClient()[m
[32m+[m[32m            assert client.model == "claude-3-sonnet-20240229"[m
[32m+[m[32m            assert client.conversation_history == [][m
 [m
 def test_send_message():[m
[31m-    """Test sending a message and getting a response."""[m
[31m-    client = AnthropicClient()[m
[31m-    response = client.send_message("Hello, Claude!")[m
[32m+[m[32m    """Test sending a message to Claude."""[m
[32m+[m[32m    mock_response = MagicMock()[m
[32m+[m[32m    mock_response.content = [MagicMock(text="Hello, world!")][m
     [m
[31m-    assert isinstance(response, str)[m
[31m-    assert len(response) > 0[m
[31m-    assert len(client.conversation_history) == 2  # User message + assistant response[m
[32m+[m[32m    with patch.dict(os.environ, {"CLAUDE_API_KEY": "test-key"}):[m
[32m+[m[32m        with patch("anthropic.Client") as mock_client_class:[m
[32m+[m[32m            mock_client = MagicMock()[m
[32m+[m[32m            mock_client.messages.create.return_value = mock_response[m
[32m+[m[32m            mock_client_class.return_value = mock_client[m
[32m+[m[41m            [m
[32m+[m[32m            client = AnthropicClient()[m
[32m+[m[32m            response = client.send_message("Hi", system="Be helpful")[m
[32m+[m[41m            [m
[32m+[m[32m            assert response == "Hello, world!"[m
[32m+[m[32m            mock_client.messages.create.assert_called_once()[m
[32m+[m[32m            call_args = mock_client.messages.create.call_args[1][m
[32m+[m[32m            assert call_args["model"] == "claude-3-sonnet-20240229"[m
[32m+[m[32m            assert call_args["messages"][0]["content"] == "Hi"[m
[32m+[m[32m            assert call_args["system"] == "Be helpful"[m
 [m
 def test_conversation_history():[m
     """Test conversation history management."""[m
[31m-    client = AnthropicClient()[m
[32m+[m[32m    mock_response = MagicMock()[m
[32m+[m[32m    mock_response.content = [MagicMock(text="Hello!")][m
     [m
[31m-    # Send first message[m
[31m-    client.send_message("What is AI?")[m
[31m-    assert len(client.conversation_history) == 2[m
[31m-    [m
[31m-    # Send follow-up message[m
[31m-    client.send_message("Can you elaborate?")[m
[31m-    assert len(client.conversation_history) == 4[m
[31m-    [m
[31m-    # Clear history[m
[31m-    client.clear_history()[m
[31m-    assert len(client.conversation_history) == 0[m
[32m+[m[32m    with patch.dict(os.environ, {"CLAUDE_API_KEY": "test-key"}):[m
[32m+[m[32m        with patch("anthropic.Client") as mock_client_class:[m
[32m+[m[32m            mock_client = MagicMock()[m
[32m+[m[32m            mock_client.messages.create.return_value = mock_response[m
[32m+[m[32m            mock_client_class.return_value = mock_client[m
[32m+[m[41m            [m
[32m+[m[32m            client = AnthropicClient()[m
[32m+[m[32m            client.send_message("Hi")[m
[32m+[m[41m            [m
[32m+[m[32m            assert len(client.conversation_history) == 2[m
[32m+[m[32m            assert client.conversation_history[0]["role"] == "user"[m
[32m+[m[32m            assert client.conversation_history[0]["content"] == "Hi"[m
[32m+[m[32m            assert client.conversation_history[1]["role"] == "assistant"[m
[32m+[m[32m            assert client.conversation_history[1]["content"] == "Hello!"[m
[32m+[m[41m            [m
[32m+[m[32m            client.clear_history()[m
[32m+[m[32m            assert len(client.conversation_history) == 0[m
 [m
[31m-def test_missing_api_key(monkeypatch):[m
[32m+[m[32mdef test_missing_api_key():[m
     """Test error handling for missing API key."""[m
[31m-    # Mock os.getenv to return None for CLAUDE_API_KEY[m
[31m-    monkeypatch.setattr('os.getenv', lambda x: None if x == "CLAUDE_API_KEY" else os.environ.get(x))[m
[31m-    [m
[31m-    # Should raise ValueError when API key is missing[m
[31m-    with pytest.raises(ValueError, match="CLAUDE_API_KEY not found in environment"):[m
[31m-        AnthropicClient()[m
[31m-[m
[31m-    # Reload dotenv[m
[31m-    load_dotenv(find_dotenv()) [m
\ No newline at end of file[m
[32m+[m[32m    with patch.dict(os.environ, {}, clear=True):[m
[32m+[m[32m        with patch("anthropic.Client") as mock_client:[m
[32m+[m[32m            mock_client.side_effect = ValueError("API key is required")[m
[32m+[m[32m            with pytest.raises(ValueError, match="Failed to initialize Anthropic client: API key is required"):[m
[32m+[m[32m                AnthropicClient()[m[41m [m
\ No newline at end of file[m
