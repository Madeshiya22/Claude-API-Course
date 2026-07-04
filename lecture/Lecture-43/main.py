import re
import json
import math
import numpy as np
import voyageai
import base64
import mimetypes
import os
from collections import Counter
from datetime import datetime, timedelta

from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic.types import ToolParam, Message

load_dotenv()

client = Anthropic()

model = "claude-3-7-sonnet-20250219"


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
    return "\n".join(
        block.text for block in message.content
        if block.type == "text"
    )


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


def chat(
    messages,
    system=None,
    stop_sequences=None,
    tools=None,
    thinking=False,
    thinking_budget=1024,
):
    if stop_sequences is None:
        stop_sequences = []

    params = {
        "model": model,
        "max_tokens": 4000,
        "messages": messages,
        "stop_sequences": stop_sequences,
    }

    if system:
        params["system"] = system

    if tools:
        params["tools"] = tools

    if thinking:
        params["thinking"] = {
            "type": "enabled",
            "budget_tokens": thinking_budget,
        }

    message = client.messages.create(**params)

    return message


def run_tool(tool_name, tool_input):
    if tool_name == "get_current_datetime":
        return get_current_datetime(**tool_input)
    elif tool_name == "add_duration_to_datetime":
        return add_duration_to_datetime(**tool_input)
    elif tool_name == "set_reminder":
        return set_reminder(**tool_input)
    elif tool_name == "web_search":
        return "Dummy web search result"

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
            thinking=True,
            thinking_budget=2048,
        )

        add_assistant_message(messages, response)

        for block in response.content:
            if block.type == "thinking":
                print("\nThinking:\n")
                print(block.thinking)
            elif block.type == "redacted_thinking":
                print("\n[Thinking Hidden]\n")
            elif block.type == "text":
                print(block.text)
            elif block.type == "tool_use":
                print(f"Using Tool: {block.name}")

        if response.stop_reason != "tool_use":
            break

        tool_result_blocks = run_tools(response)

        add_user_message(messages, tool_result_blocks)

    return messages


pdf_path = "earth.pdf"

if not os.path.exists(pdf_path):
    raise FileNotFoundError(pdf_path)

if os.path.getsize(pdf_path) > 32 * 1024 * 1024:
    raise ValueError("PDF too large")

mime_type, _ = mimetypes.guess_type(pdf_path)
if mime_type is None:
    mime_type = "application/pdf"

with open(pdf_path, "rb") as f:
    file_bytes = base64.standard_b64encode(f.read()).decode("utf-8")

messages = []

add_user_message(
    messages,
    [
        {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": mime_type,
                "data": file_bytes,
            },
            "title": "earth.pdf",
            "citations": {
                "enabled": True
            }
        },
        {
            "type": "text",
            "text": "Summarize this PDF in one paragraph."
        }
    ]
)

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


with open("lecture/Lecture-39/report.md", "r", encoding="utf-8") as f:
    text = f.read()

# --- Lecture 35: Embeddings ---

voyage_client = voyageai.Client()


def generate_embedding(chunks, input_type="document", model="voyage-3-large"):
    is_list = isinstance(chunks, list)
    inputs = chunks if is_list else [chunks]

    result = voyage_client.embed(inputs, model=model, input_type=input_type)

    return result.embeddings if is_list else result.embeddings[0]


# --- Lecture 37: Vector Database (VectorIndex) ---


class VectorIndex:
    def __init__(self, embedding_fn):
        self.embedding_fn = embedding_fn
        self.vectors = []
        self.metadata = []

    def add_vector(self, vector, meta):
        self.vectors.append(vector)
        self.metadata.append(meta)

    def add_documents(self, documents):
        contents = [doc["content"] for doc in documents]
        vectors = self.embedding_fn(contents)
        for vector, document in zip(vectors, documents):
            self.add_vector(vector, document)

    def search(self, query, k=2):
        query_embedding = self.embedding_fn(query, input_type="query")
        results = []
        for i, vec in enumerate(self.vectors):
            dot_product = np.dot(query_embedding, vec)
            norm1 = np.linalg.norm(query_embedding)
            norm2 = np.linalg.norm(vec)
            if norm1 == 0 or norm2 == 0:
                sim = 0
            else:
                sim = dot_product / (norm1 * norm2)
            results.append((self.metadata[i], sim))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]


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
        return re.findall(r"\w+", text.lower())

    def add_document(self, doc):
        self.documents.append(doc)
        tokens = self._tokenize(doc["content"])
        self.doc_lengths.append(len(tokens))
        self.avgdl = sum(self.doc_lengths) / len(self.doc_lengths)
        frequencies = Counter(tokens)
        self.doc_freqs.append(frequencies)

        for token in frequencies:
            self.idf[token] = self.idf.get(token, 0) + 1

    def add_documents(self, documents):
        for doc in documents:
            self.add_document(doc)

    def _compute_idf(self):
        N = len(self.documents)
        for token, df in self.idf.items():
            self.idf[token] = math.log(1 + (N - df + 0.5) / (df + 0.5))

    def search(self, query, k=3):
        self._compute_idf()
        query_tokens = self._tokenize(query)
        scores = []
        for i, doc in enumerate(self.documents):
            score = 0
            for token in query_tokens:
                if token not in self.doc_freqs[i]:
                    continue
                tf = self.doc_freqs[i][token]
                idf = self.idf.get(token, 0)
                score += (
                    idf
                    * (tf * (self.k1 + 1))
                    / (
                        tf
                        + self.k1
                        * (1 - self.b + self.b * self.doc_lengths[i] / self.avgdl)
                    )
                )
            scores.append((doc, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:k]


# --- Lecture 39: Hybrid Search (Retriever & RRF) ---


class Retriever:
    def __init__(self, bm25_index, vector_index):
        self.bm25_index = bm25_index
        self.vector_index = vector_index

    def add_documents(self, documents):
        self.bm25_index.add_documents(documents)
        self.vector_index.add_documents(documents)

    def search(self, query, k=3):
        bm25_results = self.bm25_index.search(query, k=10)
        vector_results = self.vector_index.search(query, k=10)

        rrf_scores = {}

        for rank, (doc, _) in enumerate(bm25_results):
            content = doc["content"]
            if content not in rrf_scores:
                rrf_scores[content] = {"doc": doc, "score": 0.0}
            rrf_scores[content]["score"] += 1.0 / (rank + 1 + 60)

        for rank, (doc, _) in enumerate(vector_results):
            content = doc["content"]
            if content not in rrf_scores:
                rrf_scores[content] = {"doc": doc, "score": 0.0}
            rrf_scores[content]["score"] += 1.0 / (rank + 1 + 60)

        sorted_results = sorted(
            rrf_scores.values(), key=lambda x: x["score"], reverse=True
        )
        return [(item["doc"], item["score"]) for item in sorted_results[:k]]


chunks = chunk_by_section(text)

vector_index = VectorIndex(embedding_fn=generate_embedding)

bm25_index = BM25Index()

retriever = Retriever(bm25_index, vector_index)

retriever.add_documents([{"content": chunk} for chunk in chunks])

query = "What happened with INC-2023-Q4-011?"

results = retriever.search(query, k=3)

print("Top Matches\n")

for doc, score in results:
    print(f"Score : {score:.4f}")
    print(doc["content"])
    print("\n----------------------\n")
