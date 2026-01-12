import json
import re
import requests
from parse_openapi import parse_openapi

# -----------------------------
# Step 1: Parse OpenAPI
# -----------------------------
api_schema = parse_openapi("openapi.json")

# -----------------------------
# Step 2: Ask LLM to generate test cases (JSON)
# -----------------------------
TESTCASE_PROMPT = """
You are a senior QA automation engineer.

Given this OpenAPI schema:
{schema}

Generate API test cases in STRICT JSON format.

Rules:
- Only generate **valid payloads** according to the schema.
- Do NOT assume any fields are required unless they appear in the 'required' array.
- Only include fields defined in the schema.
- IMPORTANT: Use the exact payload structure from the schema properties, NOT nested objects.
- Only Include User and Id as per schema definitions.
- Each test case must include:
  - test_name
  - method
  - endpoint
  - payload
  - expected_status
- Include negative test cases for missing required fields and invalid data types.
- Output ONLY valid JSON
- Do NOT include explanations, comments, or markdown
"""

prompt_cases = TESTCASE_PROMPT.format(schema=json.dumps(api_schema, indent=2))

response = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "llama3", "prompt": prompt_cases, "stream": False}
)

test_cases_raw = response.json()["response"]

# -----------------------------
# Step 3: Extract JSON from LLM output
# -----------------------------
# This regex extracts the first [...] block from the response
match = re.search(r"\[.*\]", test_cases_raw, flags=re.DOTALL)
if not match:
    print("❌ Could not find JSON array in LLM response:")
    print(test_cases_raw)
    raise ValueError("No JSON found in LLM output")
print(test_cases_raw)
test_cases_json = match.group(0)

# Now safely parse
test_cases = json.loads(test_cases_json)
print(f"✅ Parsed {len(test_cases)} test cases")

# -----------------------------
# Step 4: Ask LLM to generate pytest code from test cases
# -----------------------------
PYTEST_PROMPT = """
You are a senior QA automation engineer.

Your task:
- Take the following JSON test cases and generate a complete pytest file.
- Each test case includes: test_name, method, endpoint, payload, expected_status.
- Use the `requests` library.
- Assume FastAPI is running at BASE_URL.
- Output ONLY valid Python code, ready to save as a pytest file.
- Do NOT include explanations, comments, or markdown.

Test cases JSON:
{test_cases_json}
"""

prompt_pytest = PYTEST_PROMPT.format(test_cases_json=json.dumps(test_cases, indent=2))

response_pytest = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "llama3", "prompt": prompt_pytest, "stream": False}
)

pytest_code = response_pytest.json()["response"]
pytest_code_clean = re.sub(r"^(?:\w+)?\n|$", "", pytest_code.strip(), flags=re.MULTILINE)
# -----------------------------
# Step 5: Save to pytest file
# -----------------------------
with open("test_api.py", "w") as f:
    f.write(pytest_code)

print("✅ Pytest file 'test_api.py' generated from LLM test cases!")
