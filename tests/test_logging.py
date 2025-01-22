"""Tests for prompt logging functionality."""
import os
import json
import time
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
from src.client import AnthropicClient

@pytest.fixture
def preserve_logs():
    """Fixture to ensure logs directory exists."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    yield log_dir

def test_log_file_creation(preserve_logs):
    """Test that log files are created correctly."""
    with patch.dict(os.environ, {"CLAUDE_API_KEY": "test-key"}):
        with patch("anthropic.Client") as mock_client_class:
            client = AnthropicClient()
            
            # Verify logs directory exists
            log_dir = Path("logs")
            assert log_dir.exists()
            assert log_dir.is_dir()
            
            # Verify log file was created
            log_files = list(log_dir.glob("prompt_log_*.jsonl"))
            assert len(log_files) >= 1  # At least one log file exists
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            assert latest_log.name.startswith("prompt_log_")
            assert latest_log.name.endswith(".jsonl")
            
            # Verify log file is preserved
            log_content = latest_log.read_text()
            assert log_content  # Log file has content
            assert "Client initialized" in log_content

def test_log_content(preserve_logs):
    """Test that interactions are logged correctly."""
    test_prompt = "Test prompt"
    test_response = "Test response"
    
    with patch.dict(os.environ, {"CLAUDE_API_KEY": "test-key"}):
        with patch("anthropic.Client") as mock_client_class:
            # Set up mock response
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text=test_response)]
            mock_client.messages.create.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            # Create client and send message
            client = AnthropicClient()
            client.send_message(test_prompt)
            
            # Find and read log file
            log_files = list(Path("logs").glob("prompt_log_*.jsonl"))
            assert len(log_files) >= 1
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            
            log_content = latest_log.read_text().splitlines()
            assert len(log_content) >= 2  # Init message + interaction
            
            # Parse last log entry
            last_entry = json.loads(log_content[-1])
            assert "timestamp" in last_entry
            assert "prompt" in last_entry
            assert "response_summary" in last_entry
            assert last_entry["prompt"] == test_prompt
            assert last_entry["response_summary"] == test_response

def test_tool_usage_logging(preserve_logs):
    """Test that tool usage is properly logged."""
    test_prompt = "List the contents of /test/dir"
    test_response = "Directory contents: file1.txt, file2.txt"
    test_tools = [
        {"tool": "list_dir", "args": {"path": "/test/dir"}},
        {"tool": "read_file", "args": {"path": "/test/dir/file1.txt"}},
        {"tool": "grep_search", "args": {"pattern": "test", "files": ["/test/dir"]}}
    ]
    
    with patch.dict(os.environ, {"CLAUDE_API_KEY": "test-key"}):
        with patch("anthropic.Client") as mock_client_class:
            # Set up mock response
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text=test_response)]
            mock_client.messages.create.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            # Create client and send message with tool usage
            client = AnthropicClient()
            client.send_message(test_prompt, tools_used=test_tools)
            
            # Find and read log file
            log_files = list(Path("logs").glob("prompt_log_*.jsonl"))
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            
            log_content = latest_log.read_text().splitlines()
            assert len(log_content) >= 2  # Init message + interaction
            
            # Parse last log entry
            last_entry = json.loads(log_content[-1])
            assert "tools_used" in last_entry
            assert len(last_entry["tools_used"]) == 3
            
            # Verify each tool is logged correctly
            logged_tools = last_entry["tools_used"]
            assert logged_tools[0]["tool"] == "list_dir"
            assert logged_tools[1]["tool"] == "read_file"
            assert logged_tools[2]["tool"] == "grep_search"
            
            # Verify tool arguments are logged
            assert "path" in logged_tools[0]["args"]
            assert "path" in logged_tools[1]["args"]
            assert "pattern" in logged_tools[2]["args"]

def test_multiple_tool_interactions(preserve_logs):
    """Test logging of a sequence of tool interactions."""
    interactions = [
        {
            "prompt": "Create a new file",
            "response": "File created successfully",
            "tools": [{"tool": "edit_file", "args": {"path": "test.txt", "content": "test"}}]
        },
        {
            "prompt": "Search for content",
            "response": "Found matches",
            "tools": [
                {"tool": "grep_search", "args": {"pattern": "test"}},
                {"tool": "codebase_search", "args": {"query": "test"}}
            ]
        },
        {
            "prompt": "Delete the file",
            "response": "File deleted",
            "tools": [{"tool": "delete_file", "args": {"path": "test.txt"}}]
        }
    ]
    
    with patch.dict(os.environ, {"CLAUDE_API_KEY": "test-key"}):
        with patch("anthropic.Client") as mock_client_class:
            # Set up mock response
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            # Create client and simulate multiple interactions
            client = AnthropicClient()
            
            for interaction in interactions:
                mock_response = MagicMock()
                mock_response.content = [MagicMock(text=interaction["response"])]
                mock_client.messages.create.return_value = mock_response
                
                client.send_message(interaction["prompt"], tools_used=interaction["tools"])
            
            # Find and read log file
            log_files = list(Path("logs").glob("prompt_log_*.jsonl"))
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            
            log_content = latest_log.read_text().splitlines()
            assert len(log_content) >= 4  # Init + 3 interactions
            
            # Skip init message and verify each interaction
            log_entries = [json.loads(entry) for entry in log_content[1:]]
            for i, entry in enumerate(log_entries):
                assert entry["prompt"] == interactions[i]["prompt"]
                assert entry["response_summary"] == interactions[i]["response"]
                assert len(entry["tools_used"]) == len(interactions[i]["tools"])
                
                # Verify tool details
                for j, tool in enumerate(entry["tools_used"]):
                    assert tool["tool"] == interactions[i]["tools"][j]["tool"]
                    assert "args" in tool

def test_log_rotation(preserve_logs):
    """Test that multiple sessions create separate log files."""
    with patch.dict(os.environ, {"CLAUDE_API_KEY": "test-key"}):
        with patch("anthropic.Client") as mock_client_class:
            # Record initial log count
            initial_logs = set(Path("logs").glob("prompt_log_*.jsonl"))
            
            # Create multiple clients with small delays
            clients = []
            for _ in range(3):
                clients.append(AnthropicClient())
                time.sleep(0.001)  # Small delay to ensure unique timestamps
            
            # Verify new log files were created
            current_logs = set(Path("logs").glob("prompt_log_*.jsonl"))
            new_logs = current_logs - initial_logs
            assert len(new_logs) == 3
            
            # Verify timestamps in filenames are unique
            timestamps = [f.name.split("_", 2)[2].split(".")[0] for f in new_logs]
            assert len(set(timestamps)) == 3

def test_error_logging(preserve_logs):
    """Test that errors are logged correctly."""
    with patch.dict(os.environ, {"CLAUDE_API_KEY": "test-key"}):
        with patch("anthropic.Client") as mock_client_class:
            # Set up mock to raise an error
            mock_client = MagicMock()
            mock_client.messages.create.side_effect = Exception("Test error")
            mock_client_class.return_value = mock_client
            
            # Create client and attempt to send message
            client = AnthropicClient()
            with pytest.raises(RuntimeError):
                client.send_message("Test prompt")
            
            # Verify error was logged
            log_files = list(Path("logs").glob("prompt_log_*.jsonl"))
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            
            log_content = latest_log.read_text().splitlines()
            error_entries = [
                line for line in log_content 
                if json.loads(line).get("error", "").startswith("Error sending message")
            ]
            assert len(error_entries) == 1
            assert "Test error" in error_entries[0]

def test_logs_preserved():
    """Test that log files are preserved between test runs."""
    log_dir = Path("logs")
    
    # Verify logs directory exists and contains .gitkeep
    assert log_dir.exists()
    assert log_dir.is_dir()
    assert (log_dir / ".gitkeep").exists()
    
    # Verify log files exist and have content
    log_files = list(log_dir.glob("prompt_log_*.jsonl"))
    assert len(log_files) > 0  # Log files should exist
    
    for log_file in log_files:
        assert log_file.stat().st_size > 0  # Files should have content
        content = log_file.read_text()
        assert content  # Content should be readable
        # Verify it's valid JSON lines
        for line in content.splitlines():
            entry = json.loads(line)
            assert "timestamp" in entry  # Each entry should have required fields 