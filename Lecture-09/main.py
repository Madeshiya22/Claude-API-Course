from dotenv import load_dotenv
from anthropic import Anthropic
import json

load_dotenv()

client = Anthropic()

model = "claude-sonnet-4-0"


def add_user_message(messages, text):
    messages.append({
        "role": "user",
        "content": text
    })


def add_assistant_message(messages, text):
    messages.append({
        "role": "assistant",
        "content": text
    })


def chat(messages, system=None, temperature=0.2, stop_sequences=None):

    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature
    }

    if system:
        params["system"] = system

    if stop_sequences:
        params["stop_sequences"] = stop_sequences

    message = client.messages.create(**params)

    return message.content[0].text


messages = []

add_user_message(
    messages,
    "Generate a very short AWS EventBridge rule as JSON."
)

add_assistant_message(
    messages,
    "```json"
)

text = chat(
    messages,
    stop_sequences=["```"]
)

print("\nGenerated JSON:\n")
print(text)

try:
    clean_json = json.loads(text.strip())

    print("\nParsed Python Dictionary:\n")
    print(clean_json)

except Exception as e:
    print("\nInvalid JSON")
    print(e)