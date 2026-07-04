import re
import json
import math
from collections import Counter
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


with open("lecture/Lecture-38/report.md", "r", encoding="utf-8") as f:
    text = f.read()

# --- Lecture 38: BM25 (Lexical Search) ---

class BM25Index:
    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.documents = []
        self.doc_lengths = []
        self.avgdl = 0
        self.doc_freqs = []
        self.idf = {}

    def _tokenize(self, text):
        return re.findall(r'\w+', text.lower())

    def add_document(self, doc):
        self.documents.append(doc)
        tokens = self._tokenize(doc["content"])
        self.doc_lengths.append(len(tokens))
        self.avgdl = sum(self.doc_lengths) / len(self.doc_lengths)
        frequencies = Counter(tokens)
        self.doc_freqs.append(frequencies)
        
        for token in frequencies:
            self.idf[token] = self.idf.get(token, 0) + 1

    def _compute_idf(self):
        N = len(self.documents)
        for token, df in self.idf.items():
            self.idf[token] = math.log(1 + (N - df + 0.5) / (df + 0.5))

    def search(self, query, k=3):
        query_tokens = self._tokenize(query)
        scores = []
        for i, doc in enumerate(self.documents):
            score = 0
            for token in query_tokens:
                if token not in self.doc_freqs[i]:
                    continue
                tf = self.doc_freqs[i][token]
                idf = self.idf.get(token, 0)
                score += idf * (tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * self.doc_lengths[i] / self.avgdl))
            scores.append((doc, score))
            
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:k]


chunks = chunk_by_section(text)

store = BM25Index()

for chunk in chunks:
    store.add_document(
        {
            "content": chunk
        }
    )

store._compute_idf()

query = "What happened with INC-2023-Q4-011?"

results = store.search(query, 3)

print("Top Matches\n")

for doc, score in results:
    print(f"Score : {score:.2f}")
    print(doc["content"])
    print("\n----------------------\n")
