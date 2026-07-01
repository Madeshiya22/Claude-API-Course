from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()

model = "claude-sonnet-4-0"


def add_user_message(messages, text):
    user_message = {
        "role": "user",
        "content": text
    }
    messages.append(user_message)


def add_assistant_message(messages, text):
    assistant_message = {
        "role": "assistant",
        "content": text
    }
    messages.append(assistant_message)


def chat(messages):
    message = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=messages
    )

    return message.content[0].text


messages = []

add_user_message(
    messages,
    "Define quantum computing in one sentence."
)

answer = chat(messages)

add_assistant_message(messages, answer)

add_user_message(
    messages,
    "Write another sentence."
)

final_answer = chat(messages)

print(final_answer)