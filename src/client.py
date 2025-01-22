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
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-sonnet-20240229"
    ):
        """Initialize the client with API key and model."""
        load_dotenv()
        
        if not api_key:
            api_key = os.getenv("CLAUDE_API_KEY")
            if not api_key:
                raise ValueError("API key not provided and CLAUDE_API_KEY not found in environment")
            
        try:
            # Initialize with latest Anthropic SDK
            self.client = anthropic.Client(api_key=api_key)
            self.model = model
            self.conversation_history: List[Dict[str, str]] = []
            
            # Set up logging
            self.setup_logging()
            
        except Exception as e:
            raise ValueError(f"Failed to initialize Anthropic client: {str(e)}")
    
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
        
        # Log initialization
        self.log_interaction("INIT", "Client initialized", [{"tool": "init"}])
    
    def log_interaction(self, prompt: str, response: Any, tools_used: List[Dict] = None):
        """Log a prompt-response interaction."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "response_summary": str(response)[:1000] + "..." if len(str(response)) > 1000 else str(response),
            "tools_used": tools_used or []
        }
        self.logger.info(json.dumps(log_entry))
    
    def send_message(
        self,
        message: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """Send a message to Claude and return the response."""
        try:
            # Create message request
            messages = [{"role": "user", "content": message}]
            
            # Add conversation history if any
            if self.conversation_history:
                messages = self.conversation_history + messages
            
            # Make API call
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=messages
            )
            
            # Update conversation history
            self.conversation_history.extend([
                {"role": "user", "content": message},
                {"role": "assistant", "content": response.content[0].text}
            ])
            
            # Log the interaction
            self.log_interaction(message, response.content[0].text)
            
            return response.content[0].text
            
        except Exception as e:
            error_msg = f"Error sending message: {str(e)}"
            self.logger.error(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "error": error_msg,
                "prompt": message
            }))
            raise RuntimeError(error_msg)
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
        self.log_interaction("CLEAR", "Conversation history cleared", [{"tool": "clear_history"}]) 