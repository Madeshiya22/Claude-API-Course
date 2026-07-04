import re
import json
from datetime import datetime, timedelta

from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic.types import ToolParam, Message

load_dotenv()

client = Anthropic()

model = "claude-haiku-4-5"


def add_user_message(messages, message):
    messages.append(
        {
            "role": "user",
            "content": message.content if isinstance(message, Message) else message,
        }
    )


def add_assistant_message(messages, message):
    messages.append(
        {
            "role": "assistant",
            "content": message.content if isinstance(message, Message) else message,
        }
    )


def text_from_message(message):
    return "\n".join(block.text for block in message.content if block.type == "text")


def get_current_datetime(date_format="%Y-%m-%d %H:%M:%S"):
    if not date_format:
        raise ValueError("date_format cannot be empty")

    return datetime.now().strftime(date_format)


def add_duration_to_datetime(datetime_str: str, duration: int, unit: str) -> str:
    try:
        if ":" in datetime_str:
            start = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        else:
            start = datetime.strptime(datetime_str, "%Y-%m-%d")

        kwargs = {unit: duration}
        new_date = start + timedelta(**kwargs)

        if ":" in datetime_str:
            return new_date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return new_date.strftime("%Y-%m-%d")
    except Exception as e:
        return f"Error: {str(e)}"


def set_reminder(reminder_time: str, message: str) -> str:
    print(f"\n[SYSTEM ACTION] Setting reminder: '{message}' at {reminder_time}\n")
    return f"Success: Reminder set for {reminder_time} with message: '{message}'"


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


add_duration_to_datetime_schema = ToolParam(
    {
        "name": "add_duration_to_datetime",
        "description": "Adds a duration to a starting date/time.",
        "input_schema": {
            "type": "object",
            "properties": {
                "datetime_str": {
                    "type": "string",
                    "description": "The starting date/time in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format.",
                },
                "duration": {
                    "type": "integer",
                    "description": "The amount of time to add.",
                },
                "unit": {
                    "type": "string",
                    "enum": ["days", "hours", "weeks"],
                    "description": "The unit of the duration (e.g., 'days', 'hours', 'weeks').",
                },
            },
            "required": ["datetime_str", "duration", "unit"],
        },
    }
)


set_reminder_schema = ToolParam(
    {
        "name": "set_reminder",
        "description": "Sets a reminder for a specific date/time with a message.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reminder_time": {
                    "type": "string",
                    "description": "The date and time for the reminder, e.g. YYYY-MM-DD HH:MM:SS or YYYY-MM-DD.",
                },
                "message": {"type": "string", "description": "The reminder message."},
            },
            "required": ["reminder_time", "message"],
        },
    }
)

web_search_schema = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 5,
}


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
    elif tool_name == "add_duration_to_datetime":
        return add_duration_to_datetime(**tool_input)
    elif tool_name == "set_reminder":
        return set_reminder(**tool_input)

    raise ValueError(f"Unknown tool: {tool_name}")


def run_tools(message):
    tool_requests = [block for block in message.content if block.type == "tool_use"]

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
            tools=[
                get_current_datetime_schema,
                add_duration_to_datetime_schema,
                set_reminder_schema,
                web_search_schema,
            ],
        )

        add_assistant_message(messages, response)

        print(text_from_message(response))

        if response.stop_reason != "tool_use":
            break

        tool_result_blocks = run_tools(response)

        add_user_message(messages, tool_result_blocks)

    return messages


messages = []
add_user_message(messages, "What's the best exercise for gaining leg muscle?")

conversation = run_conversation(messages)

print("\n--- Final Conversation History ---")
for message in conversation:
    print(message)

# --- Lecture 34: Text Chunking Strategies ---


def chunk_by_char(text, chunk_size=150, chunk_overlap=20):
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i : i + chunk_size]
        chunks.append(chunk)
        i += chunk_size - chunk_overlap
    return chunks


def chunk_by_sentence(text, max_sentences_per_chunk=5, overlap_sentences=1):
    sentences = re.split(r"(?<=[.!?]) +", text)
    chunks = []
    i = 0
    while i < len(sentences):
        chunk = sentences[i : i + max_sentences_per_chunk]
        chunks.append(" ".join(chunk))
        if i + max_sentences_per_chunk >= len(sentences):
            break
        i += max_sentences_per_chunk - overlap_sentences
    return chunks


def chunk_by_section(document_text):
    pattern = r"\n## "
    return re.split(pattern, document_text)


with open("lecture/Lecture-35/report.md", "r", encoding="utf-8") as f:
    text = f.read()

print("\n--- Testing chunk_by_section ---")
for chunk in chunk_by_section(text):
    print(chunk)
    print("----")

print("\n--- Testing chunk_by_sentence ---")
for chunk in chunk_by_sentence(text):
    print(chunk)
    print("----")

print("\n--- Testing chunk_by_char ---")
for chunk in chunk_by_char(text):
    print(chunk)
    print("----")

# --- Lecture 35: Embeddings ---

import voyageai

voyage_client = voyageai.Client()


def generate_embedding(text, model="voyage-3-large", input_type="query"):
    result = voyage_client.embed([text], model=model, input_type=input_type)
    return result.embeddings[0]


chunks = chunk_by_section(text)
embedding = generate_embedding(chunks[0])

print("\n--- Testing Embeddings ---")
print("First Chunk Embedding Length:", len(embedding))
print("First 5 values:", embedding[:5])
