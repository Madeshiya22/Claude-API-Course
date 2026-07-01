from dotenv import load_dotenv
from anthropic import Anthropic
import os

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

client = Anthropic(api_key=api_key)

try:
    message = client.messages.create(
        model="claude-sonnet-4-0",
        max_tokens=20,
        messages=[
            {
                "role": "user",
                "content": "Hi"
            }
        ]
    )

    print(message.content[0].text)

except Exception as e:
    print(e)