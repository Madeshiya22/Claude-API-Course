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


def chat(messages, system=None):

    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
    }

    if system:
        params["system"] = system

    message = client.messages.create(**params)

    return message.content[0].text


messages = []

system_prompt = """
You are a patient math tutor.

Do not directly answer the student's questions.

Guide them step by step.

Give hints first.

Explain in a simple way.
"""

print("=" * 50)
print("Claude Chatbot Started")
print("Type 'exit' to quit")
print("=" * 50)

while True:

    user_input = input("\nYou: ")

    if user_input.lower() == "exit":
        print("\nGoodbye 👋")
        break

    add_user_message(messages, user_input)

    try:

        answer = chat(messages, system_prompt)

        add_assistant_message(messages, answer)

        print("\nClaude:", answer)

    except Exception as e:
        print("\nError:", e)
        break