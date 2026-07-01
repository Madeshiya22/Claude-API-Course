from dotenv import load_dotenv
from anthropic import Anthropic

# Load API Key from .env
load_dotenv()

# Create Anthropic Client
client = Anthropic()

# Select Model
model = "claude-sonnet-4-0"


# Helper Function 1
# Add User Message
def add_user_message(messages, text):
    user_message = {
        "role": "user",
        "content": text
    }
    messages.append(user_message)

# Helper Function 2
# Add Assistant Message

def add_assistant_message(messages, text):
    assistant_message = {
        "role": "assistant",
        "content": text
    }
    messages.append(assistant_message)


# Helper Function 3
# Call Claude API
def chat(messages, system=None, temperature=0.2):

    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature
    }

    if system:
        params["system"] = system

    with client.messages.stream(**params) as stream:

        for text in stream.text_stream:
            print(text, end="", flush=True)

        print()

        final_message = stream.get_final_message()

        return final_message.content[0].text

# Main Chatbot
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

    # Take user input
    user_input = input("\nYou: ")

    # Exit chatbot
    if user_input.lower() == "exit":
        print("\nGoodbye 👋")
        break

    # Add user message
    add_user_message(messages, user_input)

    try:
        print("\nClaude: ", end="")

        answer = chat(messages, system_prompt,0.2)
        # Add assistant response
        add_assistant_message(messages, answer)

        # Print response



    except Exception as e:
        print("\nError:", e)
        break