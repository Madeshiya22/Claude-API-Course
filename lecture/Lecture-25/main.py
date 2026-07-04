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


def add_assistant_message(messages, text):

    assistant_message = {"role": "assistant", "content": text}

    messages.append(assistant_message)


def chat(messages, system=None, temperature=1.0, stop_sequences=None):

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

    message = client.messages.create(**params)

    return message.content[0].text


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


print(get_current_datetime())
print(get_current_datetime("%H:%M"))
print(get_current_datetime("%Y-%m-%d"))
