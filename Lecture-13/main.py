from dotenv import load_dotenv
from anthropic import Anthropic
from statistics import mean
import json

load_dotenv()

client = Anthropic()

model = "claude-haiku-4-5"


def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)


def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)


def chat(messages, system=None, temperature=1.0, stop_sequences=None):

    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature,
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


def grade_by_model(test_case, output):

    eval_prompt = f"""
You are an expert AWS code reviewer.

Your task is to evaluate the following AI-generated solution.

Original Task:
<task>
{test_case["task"]}
</task>

Solution to Evaluate:
<solution>
{output}
</solution>

Provide your evaluation as a JSON object with the following fields:

- "strengths": Array of 1-3 strengths
- "weaknesses": Array of 1-3 weaknesses
- "reasoning": Short explanation
- "score": Number between 1 and 10

Respond only with JSON.

Example:

{{
    "strengths": ["Correct syntax"],
    "weaknesses": ["Missing edge cases"],
    "reasoning": "Mostly correct solution.",
    "score": 8
}}

Keep your response concise and direct.

Example response shape:

{{
    "strengths": string[],
    "weaknesses": string[],
    "reasoning": string,
    "score": number
}}
"""

    messages = []

    add_user_message(messages, eval_prompt)

    add_assistant_message(messages, "```json")

    eval_text = chat(messages, stop_sequences=["```"])

    return json.loads(eval_text)


def run_test_case(test_case):

    output = run_prompt(test_case)

    model_grade = grade_by_model(test_case, output)

    score = model_grade["score"]

    reasoning = model_grade["reasoning"]

    strengths = model_grade["strengths"]
    weaknesses = model_grade["weaknesses"]


    return {
        "output": output,
        "test_case": test_case,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "score": score,
        "reasoning": reasoning,
    }



def run_eval(dataset):

    results = []

    for test_case in dataset:

        result = run_test_case(test_case)

        results.append(result)

    average_score = mean([result["score"] for result in results])

    print(f"Average score: {average_score}")

    return results


with open("dataset.json", "r") as f:
    dataset = json.load(f)

results = run_eval(dataset)

print(json.dumps(results, indent=2))
