"""
Helper script to verify agent actions and API interactions.
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from src.client import AnthropicClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tests/agent_actions.log'),
        logging.StreamHandler()
    ]
)

def verify_file_content(file_path: Path, expected_content: dict) -> bool:
    """Verify file exists and contains expected content."""
    if not file_path.exists():
        logging.error(f"File not found: {file_path}")
        return False
    
    content = file_path.read_text()
    logging.info(f"File content:\n{content}")
    
    # Check timestamp format
    if "timestamp" in expected_content:
        try:
            timestamp = datetime.fromisoformat(expected_content["timestamp"])
            if "Timestamp:" not in content:
                logging.error("Timestamp not found in file")
                return False
        except ValueError as e:
            logging.error(f"Invalid timestamp format: {e}")
            return False
    
    # Check steps are present
    if "steps" in expected_content:
        for step in expected_content["steps"]:
            if step not in content:
                logging.error(f"Step not found in file: {step}")
                return False
    
    return True

def verify_api_logs(log_file: Path, expected_actions: list) -> bool:
    """Verify API logs match expected actions."""
    if not log_file.exists():
        logging.error(f"Log file not found: {log_file}")
        return False
    
    logs = log_file.read_text().splitlines()
    actions_found = []
    
    for log in logs:
        if "API Request:" in log:
            try:
                request = json.loads(log.split("API Request:", 1)[1])
                if "tool" in request:
                    actions_found.append(request)
            except json.JSONDecodeError as e:
                logging.error(f"Invalid JSON in log: {e}")
                continue
    
    if len(actions_found) != len(expected_actions):
        logging.error(f"Expected {len(expected_actions)} actions, found {len(actions_found)}")
        return False
    
    for expected, found in zip(expected_actions, actions_found):
        if expected["tool"] != found["tool"]:
            logging.error(f"Tool mismatch: expected {expected['tool']}, found {found['tool']}")
            return False
    
    return True

def main():
    """Run verification of agent actions."""
    # Expected content and actions
    expected_content = {
        "timestamp": datetime.now().isoformat(),
        "steps": [
            "Located testing directory",
            "Created hello-world.txt",
            "Wrote timestamp and steps"
        ]
    }
    
    expected_actions = [
        {"tool": "list_dir", "args": {"path": "."}},
        {"tool": "file_search", "args": {"query": "testing"}},
        {"tool": "list_dir", "args": {"path": "testing"}},
        {"tool": "write_file", "args": {"path": "testing/hello-world.txt"}}
    ]
    
    # Verify file content
    output_file = Path("testing/hello-world.txt")
    if not verify_file_content(output_file, expected_content):
        logging.error("File content verification failed")
        return 1
    
    # Verify API logs
    log_file = Path("tests/agent_actions.log")
    if not verify_api_logs(log_file, expected_actions):
        logging.error("API log verification failed")
        return 1
    
    logging.info("All verifications passed successfully")
    return 0

if __name__ == "__main__":
    exit(main()) 