"""
Anthropic API client wrapper with tool integration support.
"""
from typing import List, Dict, Any, Optional, Union
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import anthropic
import time

class AnthropicClient:
    """Wrapper for Anthropic API client with tool integration."""
    
    def __init__(self, api_key: str = None):
        """Initialize the client.

        Args:
            api_key: Optional API key. If not provided, will look for CLAUDE_API_KEY environment variable.
        """
        # Get API key from environment if not provided
        if not api_key:
            api_key = os.getenv("CLAUDE_API_KEY")
            if not api_key:
                raise ValueError("No API key provided. Set CLAUDE_API_KEY environment variable or pass api_key to constructor.")

        # Initialize client with latest SDK
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-sonnet-20240229"  # Latest Claude 3 model
        self.conversation_history = []

        # Set up logging
        self.setup_logging()

        # Log initialization
        self.log_interaction({
            "timestamp": datetime.now().isoformat(),
            "prompt": "INIT",
            "response_summary": "Client initialized",
            "tools_used": [{"tool": "init"}]
        })
    
    def setup_logging(self):
        """Set up logging configuration for prompts and responses."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create a unique log file for this session
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Add microseconds to ensure uniqueness
        timestamp = f"{timestamp}_{int(time.time() * 1000000) % 1000000}"
        log_file = log_dir / f"prompt_log_{timestamp}.jsonl"
        
        # Configure logger
        self.logger = logging.getLogger(f"AnthropicClient_{timestamp}")
        self.logger.setLevel(logging.INFO)
        
        # Add file handler with custom formatter
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(message)s'))  # Just the message
        self.logger.addHandler(handler)
    
    def log_interaction(self, data: Dict):
        """Log an interaction with the client.

        Args:
            data: Dictionary containing interaction data including timestamp, prompt, response, etc.
        """
        self.logger.info(json.dumps(data))
    
    def send_message(self, prompt: str, tools_used: List[Dict] = None, tool_responses: List[str] = None) -> str:
        """Send a message to the Claude API and log the interaction.
        
        Args:
            prompt: The message to send
            tools_used: List of tools used in processing this message, each with name and args
            tool_responses: List of responses from tools used
        
        Returns:
            The response from Claude
            
        Raises:
            RuntimeError: If there is an error sending the message
        """
        try:
            # Format tool usage history (limit to last 3 tools)
            tool_history = ""
            if tools_used:
                tool_history = "\nRecent tools used:\n"
                for tool in tools_used[-3:]:
                    tool_history += f"- {tool['name']}\n"
            
            # Format tool responses (limit to last response)
            response_history = ""
            if tool_responses:
                response_history = "\nLast tool response:\n" + tool_responses[-1]
            
            # Create system prompt that enables tool usage
            system_prompt = f"""You are a powerful agentic AI coding assistant with access to filesystem tools. You have direct access to these tools and MUST use them to explore and analyze code repositories. The tools are already set up and ready to use - you just need to call them.

Available tools that you can and should use RIGHT NOW:
- list_dir: Lists contents of a directory
- read_file: Reads contents of a file  
- grep_search: Searches for patterns in files
- file_search: Searches for files by name
- codebase_search: Semantic search across the codebase

You MUST use these tools to gather information. Do not say you don't have access - you do! Start by using list_dir(".") to see what's available.
{tool_history}
{response_history}"""
            
            # Format conversation history (limit to last 3 messages)
            history = ""
            for msg in self.conversation_history[-6:]:
                if msg["role"] == "user":
                    history += f"\n\nHuman: {msg['content']}"
                else:
                    history += f"\n\nAssistant: {msg['content']}"
            
            # Create message using SDK v0.7.7 format
            response = self.client.completions.create(
                model=self.model,
                prompt=f"{system_prompt}\n\n{history}\n\nHuman: {prompt}\n\nAssistant:",
                max_tokens_to_sample=1024,
                temperature=0
            )
            response_text = response.completion
            
            # Add message to conversation history
            self.conversation_history.extend([
                {
                    "role": "user",
                    "content": prompt
                },
                {
                    "role": "assistant", 
                    "content": response_text
                }
            ])
            
            # Log the interaction
            self.log_interaction({
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "response_summary": response_text,
                "tools_used": tools_used or [],
                "tool_responses": tool_responses or []
            })
            
            return response_text
            
        except Exception as e:
            error_msg = f"Error sending message: {str(e)}"
            # Log the error
            self.log_interaction({
                "timestamp": datetime.now().isoformat(),
                "error": error_msg,
                "prompt": prompt
            })
            raise RuntimeError(error_msg)
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
        self.log_interaction("CLEAR", "Conversation history cleared", [{"tool": "clear_history"}]) 