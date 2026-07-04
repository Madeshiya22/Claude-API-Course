from datetime import datetime

from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic.types import ToolParam

load_dotenv()

client = Anthropic()

model = "claude-haiku-4-5"


def add_user_message(messages, text):

    user_message = {"role": "user", "content": text}

    messages.append(user_message)


def add_assistant_message(messages, content):

    assistant_message = {"role": "assistant", "content": content}

    messages.append(assistant_message)


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


def chat(messages, system=None, temperature=1.0, stop_sequences=None):

    if stop_sequences is None:
        stop_sequences = []

    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
        "tools": [get_current_datetime_schema],
    }

    if system:
        params["system"] = system

    message = client.messages.create(**params)

    return message


messages = []
add_user_message(messages, "What time is it?")
response = chat(messages)
add_assistant_message(messages, response.content)

tool_use = None
for block in response.content:
    if block.type == "tool_use":
        tool_use = block
        break

if tool_use:
    tool_result = get_current_datetime(
        **tool_use.input
    )

    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": tool_result,
                    "is_error": False,
                }
            ],
        }
    )

response = chat(messages)

add_assistant_message(messages, response.content)

print(response.content[0].text)
