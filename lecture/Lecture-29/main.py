import json
from datetime import datetime

from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic.types import ToolParam, Message

load_dotenv()

client = Anthropic()

model = "claude-haiku-4-5"


def add_user_message(messages, message):
    messages.append({
        "role": "user",
        "content": message.content if isinstance(message, Message) else message
    })


def add_assistant_message(messages, message):
    messages.append({
        "role": "assistant",
        "content": message.content if isinstance(message, Message) else message
    })


def text_from_message(message):
    return "\n".join(
        block.text
        for block in message.content
        if block.type == "text"
    )


def get_current_datetime(date_format="%Y-%m-%d %H:%M:%S"):
    if not date_format:
        raise ValueError("date_format cannot be empty")

    return datetime.now().strftime(date_format)


get_current_datetime_schema = ToolParam(
    {
        "name": "get_current_datetime",
        "description": (
            "Returns the current date and time formatted according to the specified format. "
            "Use this tool whenever the user asks for the current date or time or when another tool "
            "needs the current datetime. The tool returns the formatted datetime string using "
            "Python's strftime format."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "date_format": {
                    "type": "string",
                    "description": (
                        "Python strftime format string used to format the returned datetime. "
                        "Example: '%Y-%m-%d %H:%M:%S' or '%H:%M'."
                    ),
                    "default": "%Y-%m-%d %H:%M:%S",
                }
            },
            "required": [],
        },
    }
)


def chat(messages, system=None, temperature=1.0, stop_sequences=None, tools=None):
    if stop_sequences is None:
        stop_sequences = []

    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }

    if system:
        params["system"] = system
        
    if tools:
        params["tools"] = tools

    message = client.messages.create(**params)

    return message


def run_tool(tool_name, tool_input):
    if tool_name == "get_current_datetime":
        return get_current_datetime(**tool_input)

    raise ValueError(f"Unknown tool: {tool_name}")


def run_tools(message):
    tool_requests = [
        block
        for block in message.content
        if block.type == "tool_use"
    ]

    tool_result_blocks = []

    for tool_request in tool_requests:
        try:
            tool_output = run_tool(tool_request.name, tool_request.input)
            tool_result_blocks.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_request.id,
                    "content": json.dumps(tool_output),
                    "is_error": False,
                }
            )
        except Exception as e:
            tool_result_blocks.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_request.id,
                    "content": json.dumps({"error": str(e)}),
                    "is_error": True,
                }
            )

    return tool_result_blocks


def run_conversation(messages):
    while True:
        response = chat(
            messages,
            tools=[get_current_datetime_schema]
        )

        add_assistant_message(messages, response)

        print(text_from_message(response))

        if response.stop_reason != "tool_use":
            break

        tool_result_blocks = run_tools(response)

        add_user_message(
            messages,
            tool_result_blocks
        )

    return messages


messages = []
add_user_message(messages, "What time is it?")
run_conversation(messages)
