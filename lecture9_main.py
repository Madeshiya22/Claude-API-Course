from dotenv import load_dotenv
from anthropic import Anthropic
import json

# Load API Key
load_dotenv()

# Create Client
client = Anthropic()

# Select Model
model = "claude-sonnet-4-0"


# Helper Function 1
# Add User Message
def add_user_message(messages, text):
    messages.append({
        "role": "user",
        "content": text
    })

# Helper Function 2
# Add Assistant Message
def add_assistant_message(messages, text):
    messages.append({
        "role": "assistant",
        "content": text
    })


# Helper Function 3
# Chat Function
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


# Main Program
messages = []

# User Prompt
add_user_message(messages,"Generate a very short AWS EventBridge rule as JSON.")

# Assistant Prefill
add_assistant_message(messages, "```json")

# Claude Response
text = chat(messages,stop_sequences=["```"])

print("\nGenerated JSON:\n")
print(text )

# Convert JSON String to Python Object
try:
    clean_json = json.loads(text.strip())

    print("\nParsed Python Dictionary:\n")
    print(clean_json)

except Exception as e:
    print("\nInvalid JSON")
    print(e)
    