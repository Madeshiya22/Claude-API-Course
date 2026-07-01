# .env se variables load karne ke liye
from dotenv import load_dotenv
# Claude API ke liye
from anthropic import Anthropic
# Env variables read karne ke liye
import os

# .env file ko load karo
load_dotenv()

# API key fetch karo
api_key = os.getenv("ANTHROPIC_API_KEY")

# API client setup karo
client = Anthropic(api_key=api_key)

try:
    # Claude ko message bhejo
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620", # Latest model
        max_tokens=20, # Answer ki max length
        messages=[ 
            {
                "role": "user", 
                "content": "Hi" # Humara message
            }
        ]
    )

    # AI ka response print karo
    print(message.content[0].text)

except Exception as e:
    # Error aane par print karo
    print(e)