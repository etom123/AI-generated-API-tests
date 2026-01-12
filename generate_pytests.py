import json
import requests
from parse_openapi import parse_openapi

# -----------------------------
# Step 1: Parse OpenAPI
# -----------------------------
api_schema = parse_openapi("openapi.json")

# -----------------------------
# Step 2: Build Agent Prompt
# -----------------------------
PROMPT_TEMPLATE = """
You are a senior QA automation engineer.

Your task:
- Read the following OpenAPI schema.
- Generate a complete pytest file that tests all endpoints.
- IMPORTANT: Use the exact payload structure from the schema properties, NOT nested objects.
- For /users POST endpoint, send payload like: {"name": "John Doe", "age": 30}
- Do NOT wrap payload in additional objects like {"User": {...}}
- Include:
  - test function names
  - correct HTTP method (GET, POST, etc.)
  - request payloads (example values for required fields)
  - assertions on expected status codes
- Use the `requests` library.
- Assume FastAPI is running at BASE_URL = 'http://localhost:8000'.
- Output ONLY valid Python code, ready to save as a pytest file.
- Do NOT include explanations, comments, or markdown.

OpenAPI Schema:
{schema}
"""

prompt = PROMPT_TEMPLATE.format(schema=json.dumps(api_schema, indent=2))

# -----------------------------
# Step 3: Ask LLM to generate pytest code
# -----------------------------
response = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "llama3", "prompt": prompt, "stream": False}
)

pytest_code = response.json()["response"]

# -----------------------------
# Step 4: Save to pytest file
# -----------------------------
with open("test_api.py", "w") as f:
    f.write(pytest_code)

print("✅ Pytest file 'test_api.py' generated directly by LLM!")
