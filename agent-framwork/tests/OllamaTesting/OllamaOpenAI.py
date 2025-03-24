import src.tools.execute_command.definitions
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv() 

def convert_format(input_json):
    print('input_json: ', input_json)
    return {
        'type': 'function',
        'name': input_json['name'],
        'description': input_json['description'],
        'parameters': input_json['parameters']
    }


if __name__ == "__main__":
    tool_definitions = src.tools.execute_command.definitions.DEFINITIONS
    converted_tools = [] 
    name_function_map = {}
    
    for tool_name in tool_definitions:
        converted_tool = convert_format(tool_definitions[tool_name])
        converted_tools.append(converted_tool) 
        name_function_map[tool_name] = tool_definitions[tool_name]['function']
    print(converted_tools) 
    messages = [{'role':'system', 'content':
                'Please use Function calling to solve the issues. '},
        {'role': 'user', 'content':
                'I want to list the current directory'}]
    print('converted_tools: ', converted_tools)

    print("INPUT messages: ", messages)

    client = OpenAI(
        base_url = 'http://localhost:11434/v1',
        api_key='ollama', # required, but unused
    )
    completion = client.chat.completions.create(
        model='deepseek-r1',
        messages=messages,
        functions=converted_tools,
    )
    print('completion: ', completion)
    openAIKey = os.getenv('OPENAI_API_KEY')
    client2 = OpenAI(
        base_url = 'https://api.openai.com/v1',
        api_key=openAIKey, # required, but unused
    )
    completion2 = client2.chat.completions.create(
        model='gpt-4o-mini',
        messages=messages,
        functions=converted_tools,
    )
    print('completion2: ', completion2)
        # print('completion: ', completion)
        # if completion.choices[0].message.tool_calls:
        #     tool_call = completion.choices[0].message.tool_calls[0]
        #     tool_name = tool_call.function.name
        #     tool_input = tool_call.function.arguments
        #     result = name_function_map[tool_name](**tool_input)
        #     print("EXECUTED TOOL result: ", result)
        #     print('completion.choices[0].message: ', completion.choices[0].message)
        #     messages.append(completion.choices[0].message)
        #     messages.append({'role': 'tool', 'content': str(result), 'name': tool_name})

        # else:
        #     print(completion.choices[0].message.content)
        #     break;
        # print()


