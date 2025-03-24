import src.tools.execute_command.definitions
import ollama



def convert_format(input_json):
    return {
        'type': 'function',
        'function': {
            'name': input_json['name'],
            'description': input_json['description'],
            'parameters': input_json['parameters']
        }
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
    while True:
        print("INPUT messages: ", messages)
        response = ollama.chat(
            model='llama3.2',
            messages=messages,
            tools=converted_tools,
        )
       
        if 'tool_calls' in response['message'] and response['message']['tool_calls']:
            tool_call = response['message']['tool_calls'][0]
            tool_name = tool_call['function']['name']
            tool_input = tool_call['function']['arguments']
            result = name_function_map[tool_name](**tool_input)
            print("EXECUTED TOOL result: ", result)
            messages.append(response['message'])
            messages.append({'role': 'tool', 'content': str(result), 'name': tool_name})

        else:
            print(response['message']['content'])
            break;
        print()


