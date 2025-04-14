import ollama
import src.tools.execute_command.definitions

def convert_format(input_json):
    return {
        'type': 'function',
        'function': {
            'name': input_json['name'],
            'description': input_json['description'],
            'parameters': input_json['parameters']
        }
    }

def run(model: str, question: str):
    client = ollama.Client()

    # Initialize conversation with a user query
    messages = [{"role": "system", "content": "You need to keep using the tools to solve the issues. If the tool is not working, please retry and use the tool again with another command! "}, {"role": "user", "content": question}]
    tool_definitions = src.tools.execute_command.definitions.DEFINITIONS
    converted_tools = [] 
    name_function_map = {}
    for tool_name in tool_definitions:
        converted_tool = convert_format(tool_definitions[tool_name])
        converted_tools.append(converted_tool) 
        name_function_map[tool_name] = tool_definitions[tool_name]['function']
    print(converted_tools) 
    # First API call: Send the query and function description to the model
    while True:
        print("LOOPING WITH MESSAGES: ", messages)
        response = client.chat(
            model=model,
            messages=messages,
            tools=converted_tools,
        )

        # Add the model's response to the conversation history
        messages.append(response["message"])

        # Check if the model decided to use the provided function

        if not response["message"].get("tool_calls"):
            print("The model didn't use the function. Its response was:")
            print(response["message"]["content"])
            return

        # Process function calls made by the model
        if response["message"].get("tool_calls"):
            

            for tool in response["message"]["tool_calls"]:
                print(tool)
                function_to_call = name_function_map[tool["function"]["name"]]
                function_args = tool["function"]["arguments"]
                function_response = function_to_call(**function_args)
                if not function_response.get('success'):
                    messages.append(
                        {
                            "role": "tool",
                            "content": str(function_response)+" Please retry and use the tool again with another command! ",
                        }
                    )
                else:
                    # Add function response to the conversation
                    messages.append(
                            {
                            "role": "tool",
                            "content": str(function_response),
                        }
                    )
                # print("MESSAGES: ", messages)
        else:
            print("The model didn't use the function. Its response was:")
            print(response["message"]["content"])
            return
    # Second API call: Get final response from the model
    # final_response = client.chat(model=model, messages=messages)

    # print(final_response["message"]["content"])
if __name__ == "__main__":
    run("llama3.2", "I want to list the current directory")

