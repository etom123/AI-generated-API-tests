from parse_openapi import parse_openapi
import json
import requests

# 1. Parse OpenAPI
api_schema = parse_openapi("openapi.json")

# 2. Build prompt
PROMPT_TEMPLATE = """
You are a senior QA automation engineer.

Given this API schema:
{schema}

Generate API test cases in STRICT JSON format.

Each test case must include:
- test_name
- payload
- expected_status

Rules:
- Output ONLY valid JSON
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include comments
"""

prompt = PROMPT_TEMPLATE.format(schema=json.dumps(api_schema, indent=2))

# 3. Send prompt to Ollama
response = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "llama3", "prompt": prompt, "stream": False}
)

# 4. Parse output
tests = json.loads(response.json()["response"])
print(json.dumps(tests, indent=2))
