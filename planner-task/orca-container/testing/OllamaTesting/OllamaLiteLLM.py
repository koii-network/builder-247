# !pip install litellm python-dotenv

import os
import litellm
import src.tools.execute_command.definitions


import json

def convert_format(input_json):
    return {
        'type': 'function',
        'function': {
            'name': input_json['name'],
            'description': input_json['description'],
            'parameters': input_json['parameters']
        }
    }

def completion(model, question):
    max_turns = 10  # Prevent infinite loops
    final_response = None

    messages = [
        {
            'role': 'user',
            'content': question
        }
    ]
    tool_definitions = src.tools.execute_command.definitions.DEFINITIONS
    converted_tools = [] 
    name_function_map = {}
    for tool_name in tool_definitions:
        converted_tool = convert_format(tool_definitions[tool_name])
        converted_tools.append(converted_tool) 
        name_function_map[tool_name] = tool_definitions[tool_name]['function']
    print("CONVERTED TOOLS: ", converted_tools)
    while max_turns > 0 and final_response is None:
        
        print("Total messages in the context:", len(messages))
        try:
            params = {
                "model": model,
                "messages": messages,
                "tools": converted_tools
            }
            print("PARAMS: ", params)
            response = litellm.completion(**params)
            print("RESPONSE: ", response)
        except KeyError as e:
            print(f"KeyError encountered: {e}")
            print("Please check the structure of the response or update the litellm library.")
            raise
        
        try:
            message = response.choices[0].message
        except KeyError as e:
            print("KeyError encountered:", e)
            print("Response content:", response)
            raise
   
        if hasattr(message, 'tool_calls') and message.tool_calls:
            messages.append(message)
            
            for tool_call in message.tool_calls:
                print("Calling tool:", tool_call.function.name, "with parameters:", tool_call.function.arguments)
                if tool_call.function.name in name_function_map and tool_call.type == "function":
                    arguments = json.loads(tool_call.function.arguments)
                    print("ARGUMENTS: ", arguments)
                    result = name_function_map[tool_call.function.name](**arguments)
                    print("RESULT: ", result)
                    messages.append({
                        "role": "tool",
                        "name": tool_call.function.name,
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    })
                    if result.get('success', False):
                        return result['stdout']
                else:
                    raise Exception(f"Invalid tool call: {tool_call.function}")
        else:
            return message.content
        max_turns -= 1
    print("Messages Transcript: ", messages)    
    raise Exception("tired of looping, failed!")
    
    
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

for model in [
    # "ollama/qwen2.5:32b",
    "ollama/llama3.1:8b",
    # "ollama/deepseek-r1:7b",
]:
    print("\n---\nTrying model:", model)
    t0 = datetime.now()
    try:
        print(
            completion(
                model=model,
                question="List the files in the current directory"
            )
        )
        print("Time taken:", datetime.now() - t0)
    except Exception as e:
        print("Error:", str(e))    