# Imports

import json
import concurrent.futures
from statistics import mean

from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()

model = "claude-haiku-4-5"


def add_user_message(messages, text):

    user_message = {"role": "user", "content": text}

    messages.append(user_message)


def add_assistant_message(messages, text):

    assistant_message = {"role": "assistant", "content": text}

    messages.append(assistant_message)


def chat(messages, system=None, temperature=1.0, stop_sequences=[]):

    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }

    if system:
        params["system"] = system

    message = client.messages.create(**params)

    return message.content[0].text


# Report Builder


def generate_prompt_evaluation_report(evaluation_results):

    total_tests = len(evaluation_results)

    scores = [result["score"] for result in evaluation_results]

    avg_score = mean(scores) if scores else 0

    max_possible_score = 10

    pass_rate = (
        100 * len([s for s in scores if s >= 7]) / total_tests if total_tests else 0
    )

    html = f"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>Prompt Evaluation Report</title>

<style>

body {{
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 20px;
    color: #333;
}}

.header {{
    background-color: #f0f0f0;
    padding: 20px;
    border-radius: 5px;
    margin-bottom: 20px;
}}

.summary-stats {{
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
}}

.stat-box {{
    background-color: #fff;
    border-radius: 5px;
    padding: 15px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    flex-basis: 30%;
    min-width: 200px;
}}

.stat-value {{
    font-size: 24px;
    font-weight: bold;
    margin-top: 5px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}}

th {{
    background-color: #4a4a4a;
    color: white;
    text-align: left;
    padding: 12px;
}}

td {{
    padding: 10px;
    border-bottom: 1px solid #ddd;
    vertical-align: top;
}}

tr:nth-child(even) {{
    background-color: #f9f9f9;
}}

.output-cell {{
    white-space: pre-wrap;
}}

.score {{
    font-weight: bold;
    padding: 5px 10px;
    border-radius: 3px;
    display: inline-block;
}}

.score-high {{
    background-color: #c8e6c9;
    color: #2e7d32;
}}

.score-medium {{
    background-color: #fff9c4;
    color: #f57f17;
}}

.score-low {{
    background-color: #ffcdd2;
    color: #c62828;
}}

.output {{
    overflow: auto;
    white-space: pre-wrap;
}}

.output pre {{
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 10px;
    margin: 0;
    font-family: Consolas, Monaco, Courier New, monospace;
    font-size: 14px;
    line-height: 1.4;
    color: #333;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
    overflow-x: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
}}

td {{
    width: 20%;
}}

.score-col {{
    width: 80px;
}}

</style>

</head>

<body>

<div class="header">

<h1>Prompt Evaluation Report</h1>

<div class="summary-stats">

<div class="stat-box">
<div>Total Test Cases</div>
<div class="stat-value">{total_tests}</div>
</div>

<div class="stat-box">
<div>Average Score</div>
<div class="stat-value">
{avg_score:.1f} / {max_possible_score}
</div>
</div>

<div class="stat-box">
<div>Pass Rate (≥7)</div>
<div class="stat-value">
{pass_rate:.1f}%
</div>
</div>

</div>

</div>

<table>

<thead>

<tr>

<th>Scenario</th>

<th>Prompt Inputs</th>

<th>Solution Criteria</th>

<th>Output</th>

<th>Score</th>

<th>Reasoning</th>

</tr>

</thead>

<tbody>
"""

    for result in evaluation_results:

        prompt_inputs_html = "<br>".join(
            [
                f"<strong>{key}:</strong> {value}"
                for key, value in result["test_case"]["prompt_inputs"].items()
            ]
        )

        criteria_string = "<br>• ".join(result["test_case"]["solution_criteria"])

        score = result["score"]

        if score >= 8:
            score_class = "score-high"

        elif score <= 5:
            score_class = "score-low"

        else:
            score_class = "score-medium"

        html += f"""
<tr>

<td>
{result["test_case"]["scenario"]}
</td>

<td class="prompt-inputs">
{prompt_inputs_html}
</td>

<td class="criteria">
• {criteria_string}
</td>

<td class="output">
<pre>{result["output"]}</pre>
</td>

<td class="score-col">
<span class="score {score_class}">
{score}
</span>
</td>

<td class="reasoning">
{result["reasoning"]}
</td>

</tr>
"""

    html += """
        </tbody>
    </table>

</body>

</html>
"""

    return html


class PromptEvaluator:

    def __init__(self, max_concurrent_tasks=3):

        self.max_concurrent_tasks = max_concurrent_tasks

    def generate_unique_ideas(self, task_description, num_cases):

        prompt = f"""
Generate {num_cases} different scenarios for the following task.

Task:
{task_description}

Return only a JSON array of short scenario descriptions.
"""

        messages = []

        add_user_message(messages, prompt)

        ideas = chat(messages)

        try:
            return json.loads(ideas)
        except json.JSONDecodeError:
            return []

    def generate_test_case(self, scenario, prompt_inputs_spec):

        prompt = f"""
    Create a JSON test case for the following scenario.

    Scenario:
    {scenario}

    Prompt Inputs:

    {json.dumps(prompt_inputs_spec, indent=2)}

    Return JSON with:

    - scenario
    - prompt_inputs
    - solution_criteria
    """

        messages = []

        add_user_message(messages, prompt)

        text = chat(messages)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "scenario": scenario,
                "prompt_inputs": prompt_inputs_spec,
                "solution_criteria": [],
            }

    def generate_dataset(
        self,
        task_description,
        prompt_inputs_spec,
        output_file,
        num_cases=3,
    ):

        scenarios = self.generate_unique_ideas(task_description, num_cases)

        dataset = []

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_concurrent_tasks
        ) as executor:

            futures = []

            for scenario in scenarios:

                future = executor.submit(
                    self.generate_test_case, scenario, prompt_inputs_spec
                )

                futures.append(future)

            for future in concurrent.futures.as_completed(futures):

                dataset.append(future.result())

        with open(output_file, "w") as f:

            json.dump(dataset, f, indent=2)

        return dataset

    def grade_output(self, test_case, output, extra_criteria=None):

        eval_prompt = f"""
    You are evaluating an AI generated response.

    Scenario:
    {test_case["scenario"]}

    Prompt Inputs:
    {json.dumps(test_case["prompt_inputs"], indent=2)}

    Evaluation Criteria:
    {json.dumps(test_case["solution_criteria"], indent=2)}

    AI Output:
    {output}

    Provide your evaluation as JSON with:

    - reasoning
    - score

    Respond only with JSON.
    """

        messages = []

        add_user_message(messages, eval_prompt)

        text = chat(messages)

        try:
            return json.loads(text)
        except Exception:
            return {
                "score": 0,
                "reasoning": "Invalid JSON returned by model",
            }

    def run_test_case(self, run_prompt_function, test_case, extra_criteria=None):

        output = run_prompt_function(test_case["prompt_inputs"])

        grade = self.grade_output(test_case, output, extra_criteria)

        return {
            "output": output,
            "test_case": test_case,
            "score": grade["score"],
            "reasoning": grade["reasoning"],
        }

    def run_evaluation(
        self,
        run_prompt_function,
        dataset_file,
        extra_criteria=None,
    ):

        with open(dataset_file, "r") as f:
            dataset = json.load(f)

        results = []

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_concurrent_tasks
        ) as executor:

            futures = []

            for test_case in dataset:

                future = executor.submit(
                    self.run_test_case,
                    run_prompt_function,
                    test_case,
                    extra_criteria,
                )

                futures.append(future)

            for future in concurrent.futures.as_completed(futures):

                results.append(future.result())

        average_score = mean([result["score"] for result in results])

        print(f"Average score: {average_score}")

        report = generate_prompt_evaluation_report(results)

        with open("prompt_evaluation_report.html", "w") as f:
            f.write(report)

        return results


evaluator = PromptEvaluator(max_concurrent_tasks=5)


dataset = evaluator.generate_dataset(
    task_description="Write a compact, concise 1 day meal plan for a single athlete",
    prompt_inputs_spec={
        "height": "Athlete's height in cm",
        "weight": "Athlete's weight in kg",
        "goal": "Goal of the athlete",
        "restrictions": "Dietary restrictions of the athlete",
    },
    output_file="dataset.json",
    num_cases=3,
)


def run_prompt(prompt_inputs):

    prompt = f"""
Generate a one-day meal plan for an athlete that meets their dietary restrictions.

<athlete_information>
Height: {prompt_inputs["height"]}
Weight: {prompt_inputs["weight"]}
Goal: {prompt_inputs["goal"]}
Restrictions: {prompt_inputs["restrictions"]}
</athlete_information>

Guidelines:
1. Include accurate daily calorie amount.
2. Show protein, fat, and carbohydrate amounts.
3. Specify when to eat each meal.
4. Use only foods that fit the dietary restrictions.
5. List all portion sizes in grams.
6. Keep the meal plan budget-friendly if mentioned.

Here is an example input with an ideal response.

<sample_input>
Height: 170 cm
Weight: 70 kg
Goal: Maintain fitness and improve cholesterol levels
Restrictions: High cholesterol
</sample_input>

<ideal_output>
Daily Calories: Approximately 2500 kcal

Macronutrients:
- Protein: 140g
- Fat: 70g
- Carbohydrates: 340g

Breakfast (7:00 AM):
- Oatmeal 80g
- Skim Milk 240ml
- Berries 100g

Lunch (1:00 PM):
- Grilled Chicken Breast 120g
- Brown Rice 150g
- Mixed Vegetables 100g

Dinner (7:00 PM):
- Baked Salmon 140g
- Broccoli 200g
- Quinoa 75g
</ideal_output>

This example is well-structured, includes calories, macronutrients, meal timings, portion sizes, and respects dietary restrictions.
"""

    messages = []

    add_user_message(messages, prompt)

    output = chat(messages)

    return output


results = evaluator.run_evaluation(
    run_prompt_function=run_prompt,
    dataset_file="dataset.json",
    extra_criteria="""
The output should include:

- Daily caloric total
- Macronutrient breakdown
- Meals with exact foods, portions, and timing
""",
)


print(json.dumps(results, indent=2))
