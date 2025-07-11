"""
LLM Client for autoscheduler2.

Provides functionality for parsing, tool calling, and open ended prompting
using the OpenAI API.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Type, TypeVar
from openai import AsyncOpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Type variable for Pydantic models
T = TypeVar('T', bound=BaseModel)


class LLMClient:
    """Provides functionality for parsing, tool calling, and open ended prompting."""
    
    def __init__(self):
        """Initialize the LLM client with OpenAI configuration."""
        # Set up logging
        self.logger = logging.getLogger('autoscheduler.llm.client')
        self.logger.setLevel(logging.INFO)
        
        # Create console handler if no handlers exist
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Get OpenAI configuration from environment
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.default_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        
        # Initialize AsyncOpenAI client
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        self.logger.info(f"LLMClient initialized with model: {self.default_model}")
    
    async def prompt(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        """
        Basic chat completion.
        
        Args:
            messages: List of chat completion objects [{'role': <>, 'content': <>}, ...]
            model: OpenAI model to use (defaults to OPENAI_MODEL from env)
            
        Returns:
            Completion.choices[0].message.content: String form of completion
        """
        model = model or self.default_model
        
        try:
            self.logger.debug(f"Sending prompt to {model} with {len(messages)} messages")
            
            completion = await self.client.chat.completions.create(
                model=model,
                messages=messages
            )
            
            response = completion.choices[0].message.content
            self.logger.debug(f"Received response: {response[:100]}...")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error in prompt: {e}")
            raise
    
    async def prompt_with_tools(
        self, 
        messages: List[Dict[str, str]], 
        tools: List[Dict[str, Any]],
        model: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Tool-calling functionality.
        
        Args:
            messages: List of chat completion objects [{'role': <>, 'content': <>}, ...]
            tools: List of tool functions available to agent (from openai tool config)
            model: OpenAI model to use (defaults to OPENAI_MODEL from env)
            
        Returns:
            Completion.choices[0].message.tool_calls
        """
        model = model or self.default_model
        
        try:
            self.logger.debug(f"Sending prompt with tools to {model}")
            self.logger.debug(f"Tools available: {[tool.get('function', {}).get('name', 'Unknown') for tool in tools]}")
            
            completion = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice="auto"  # Let the model decide which tool to use
            )
            
            tool_calls = completion.choices[0].message.tool_calls
            
            if tool_calls:
                self.logger.debug(f"Model requested {len(tool_calls)} tool calls")
                return [
                    {
                        "id": call.id,
                        "type": call.type,
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments
                        }
                    }
                    for call in tool_calls
                ]
            else:
                self.logger.debug("No tool calls requested by model")
                return []
                
        except Exception as e:
            self.logger.error(f"Error in prompt_with_tools: {e}")
            raise
    
    async def parse_structured(
        self,
        messages: List[Dict[str, str]],
        response_format: Type[T],
        model: Optional[str] = None
    ) -> T:
        """
        Structured output parsing using Pydantic.
        
        Args:
            messages: List of chat completion objects [{'role': <>, 'content': <>}, ...]
            response_format: Pydantic model type for parsing
            model: OpenAI model to use (defaults to OPENAI_MODEL from env)
            
        Returns:
            completion.choices[0].message.parsed: Parsed Pydantic object
        """
        model = model or self.default_model
        
        try:
            self.logger.debug(f"Sending structured prompt to {model}")
            self.logger.debug(f"Expected response format: {response_format.__name__}")
            
            completion = await self.client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                response_format=response_format
            )
            
            parsed_response = completion.choices[0].message.parsed
            
            if parsed_response:
                self.logger.debug(f"Successfully parsed response as {response_format.__name__}")
                return parsed_response
            else:
                # Fallback to manual parsing if structured output fails
                self.logger.warning("Structured output parsing failed, attempting manual parsing")
                content = completion.choices[0].message.content
                return response_format.model_validate_json(content)
                
        except Exception as e:
            self.logger.error(f"Error in parse_structured: {e}")
            raise