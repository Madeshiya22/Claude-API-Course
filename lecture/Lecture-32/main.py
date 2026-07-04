import os
import json
from datetime import datetime, timedelta

from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic.types import ToolParam, Message

load_dotenv()

client = Anthropic()

model = "claude-3-5-sonnet-20241022"


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


def get_text_edit_schema(model):
    if model.startswith("claude-3-7-sonnet"):
        return {
            "type": "text_editor_20250124",
            "name": "str_replace_editor",
        }

    elif model.startswith("claude-3-5-sonnet"):
        return {
            "type": "text_editor_20241022",
            "name": "str_replace_editor",
        }

    return None


class TextEditorTool:
    def __init__(self):
        self.history = {}

    def run(self, tool_input):
        command = tool_input.get("command")
        
        if command == "view":
            return self.view(tool_input)
        elif command == "create":
            return self.create(tool_input)
        elif command == "str_replace":
            return self.str_replace(tool_input)
        elif command == "insert":
            return self.insert(tool_input)
        elif command == "undo_edit":
            return self.undo_edit(tool_input)
        else:
            raise ValueError(f"Unknown command: {command}")

    def view(self, tool_input):
        path = tool_input.get("path")
        if not os.path.exists(path):
            return f"Error: File {path} not found."
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        view_range = tool_input.get("view_range")
        if view_range:
            start_line, end_line = view_range
            start_idx = max(0, start_line - 1)
            end_idx = min(len(lines), end_line)
            lines = lines[start_idx:end_idx]
            
        return "".join(lines)

    def create(self, tool_input):
        path = tool_input.get("path")
        file_text = tool_input.get("file_text")
        if os.path.exists(path):
            return f"Error: File {path} already exists."
        with open(path, "w", encoding="utf-8") as f:
            f.write(file_text)
        self.history[path] = ""
        return f"File {path} created successfully."

    def str_replace(self, tool_input):
        path = tool_input.get("path")
        old_str = tool_input.get("old_str")
        new_str = tool_input.get("new_str")
        if not os.path.exists(path):
            return f"Error: File {path} not found."
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if old_str not in content:
            return f"Error: old_str not found in {path}."
            
        self.history[path] = content
        new_content = content.replace(old_str, new_str)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return f"Successfully replaced text in {path}."

    def insert(self, tool_input):
        path = tool_input.get("path")
        insert_line = tool_input.get("insert_line")
        new_str = tool_input.get("new_str")
        if not os.path.exists(path):
            return f"Error: File {path} not found."
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        if insert_line < 1 or insert_line > len(lines) + 1:
            return f"Error: insert_line {insert_line} is out of bounds (1 to {len(lines) + 1})."
            
        self.history[path] = "".join(lines)
        lines.insert(insert_line - 1, new_str + "\n")
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return f"Successfully inserted text in {path}."

    def undo_edit(self, tool_input):
        path = tool_input.get("path")
        if path not in self.history:
            return f"Error: No edit history found for {path}."
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.history[path])
        return f"Successfully undid last edit in {path}."


text_editor = TextEditorTool()


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
                    "description": "The starting date/time in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format."
                },
                "duration": {
                    "type": "integer",
                    "description": "The amount of time to add."
                },
                "unit": {
                    "type": "string",
                    "enum": ["days", "hours", "weeks"],
                    "description": "The unit of the duration (e.g., 'days', 'hours', 'weeks')."
                }
            },
            "required": ["datetime_str", "duration", "unit"]
        }
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
                    "description": "The date and time for the reminder, e.g. YYYY-MM-DD HH:MM:SS or YYYY-MM-DD."
                },
                "message": {
                    "type": "string",
                    "description": "The reminder message."
                }
            },
            "required": ["reminder_time", "message"]
        }
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
    elif tool_name == "add_duration_to_datetime":
        return add_duration_to_datetime(**tool_input)
    elif tool_name == "set_reminder":
        return set_reminder(**tool_input)
    elif tool_name == "str_replace_editor":
        return text_editor.run(tool_input)

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
    tools_list = [
        get_current_datetime_schema,
        add_duration_to_datetime_schema,
        set_reminder_schema,
        get_text_edit_schema(model),
    ]
    # Filter out None schemas (in case model is unsupported)
    tools_list = [t for t in tools_list if t is not None]

    while True:
        response = chat(
            messages,
            tools=tools_list
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
add_user_message(
    messages, 
    f"Open {os.path.abspath(__file__)} and summarize it."
)

conversation = run_conversation(messages)

print("\n--- Final Conversation History ---")
for message in conversation:
    print(message)
