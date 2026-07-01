from dotenv import load_dotenv
from anthropic import Anthropic
from statistics import mean
import json
import ast
import re

# Load API Key
load_dotenv()

# Create Client
client = Anthropic()

# Select Model
model = "claude-haiku-4-5"


# Helper Functions


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

    if stop_sequences:
        params["stop_sequences"] = stop_sequences

    message = client.messages.create(**params)

    return message.content[0].text


# Generate Dataset


def generate_dataset():

    prompt = """
Generate an evaluation dataset for a prompt evaluation.

The dataset will be used to evaluate prompts that generate Python, JSON, or Regex specifically for AWS-related tasks.

Generate an array of JSON objects, each representing a task that requires Python, JSON, or a Regex to complete.

Example output:

```json
[
    {
        "task": "Description of task",
        "format": "json"
    },
    {
        "task": "Description of task",
        "format": "python"
    },
    {
        "task": "Description of task",
        "format": "regex"
    }
]
```

* Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a regular expression.
* Focus on tasks that do not require writing much code.

Please generate 3 objects.
"""

    messages = []

    add_user_message(messages, prompt)
    add_assistant_message(messages, "```json")

    text = chat(messages, stop_sequences=["```"])

    return json.loads(text)


# Generate dataset and save it
dataset = generate_dataset()

with open("dataset.json", "w") as f:
    json.dump(dataset, f, indent=2)

# Model Grader


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

Output Format

Provide your evaluation as a structured JSON object with the following fields, in this specific order:

- "strengths": An array of 1-3 key strengths
- "weaknesses": An array of 1-3 key areas for improvement
- "reasoning": A concise explanation of your overall assessment
- "score": A number between 1-10

Respond with JSON. Keep your response concise and direct.

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


# Prompt Runner


def run_prompt(test_case):

    prompt = f"""
Please solve the following task:

{test_case["task"]}

* Respond only with Python, JSON, or a plain Regex
* Do not add any comments or commentary or explanation
"""

    messages = []

    add_user_message(messages, prompt)
    add_assistant_message(messages, "```code")

    output = chat(messages, stop_sequences=["```"])

    return output


# Code Grader


def validate_json(text):

    try:
        json.loads(text.strip())
        return 10
    except json.JSONDecodeError:
        return 0


def validate_python(text):

    try:
        ast.parse(text.strip())
        return 10
    except SyntaxError:
        return 0


def validate_regex(text):

    try:
        re.compile(text.strip())
        return 10
    except re.error:
        return 0


def grade_syntax(response, test_case):

    output_format = test_case["format"]

    if output_format == "json":
        return validate_json(response)

    elif output_format == "python":
        return validate_python(response)

    elif output_format == "regex":
        return validate_regex(response)

    return 0


# Run One Test Case


def run_test_case(test_case):

    output = run_prompt(test_case)

    model_grade = grade_by_model(test_case, output)

    model_score = model_grade["score"]

    reasoning = model_grade["reasoning"]

    syntax_score = grade_syntax(output, test_case)

    score = (model_score + syntax_score) / 2

    return {
        "output": output,
        "test_case": test_case,
        "score": score,
        "reasoning": reasoning,
    }


# Run Evaluation


def run_eval(dataset):

    results = []

    for test_case in dataset:

        result = run_test_case(test_case)

        results.append(result)

    average_score = mean([result["score"] for result in results])

    print(f"Average score: {average_score}")

    return results


# Execute Evaluation

with open("dataset.json", "r") as f:
    dataset = json.load(f)

results = run_eval(dataset)

print(json.dumps(results, indent=2))
