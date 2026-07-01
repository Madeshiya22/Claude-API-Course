from dotenv import load_dotenv
from anthropic import Anthropic
import json

load_dotenv()

client = Anthropic()

model = "claude-haiku-4-5"


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


def chat(messages, system=None, temperature=1.0, stop_sequences=None):

    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature
    }

    if system:
        params["system"] = system

    if stop_sequences is not None:
        params["stop_sequences"] = stop_sequences

    message = client.messages.create(**params)

    return message.content[0].text


def run_prompt(test_case):

    prompt = f"""
Please solve the following task:

{test_case["task"]}
"""

    messages = []

    add_user_message(messages, prompt)

    output = chat(messages)

    return output


def run_test_case(test_case):

    output = run_prompt(test_case)

    score = 10

    return {
        "output": output,
        "test_case": test_case,
        "score": score
    }


def run_eval(dataset):

    results = []

    for test_case in dataset:
        result = run_test_case(test_case)
        results.append(result)

    return results


with open("dataset.json", "r") as f:
    dataset = json.load(f)


results = run_eval(dataset)

print(json.dumps(results, indent=2))