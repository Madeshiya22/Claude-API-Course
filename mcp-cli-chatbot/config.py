import os
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

# Load Anthropic API Key
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY is not set in the .env file.")

# Create Anthropic client
client = Anthropic(api_key=ANTHROPIC_API_KEY)
