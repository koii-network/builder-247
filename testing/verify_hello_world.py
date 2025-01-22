#!/usr/bin/env python3
"""
Verification script for hello world example.
Tests basic functionality of the Anthropic client.
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.client import AnthropicClient

def main():
    """Run hello world verification."""
    # Ensure output directory exists
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize client
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        print("Error: CLAUDE_API_KEY environment variable not set")
        sys.exit(1)
        
    client = AnthropicClient(api_key=api_key)
    
    # Send test message
    response = client.send_message("Say hello world!")
    
    # Write output
    output_file = output_dir / "hello_world_output.txt"
    output_file.write_text(response)
    print(f"Output written to: {output_file}")

if __name__ == "__main__":
    main() 