import subprocess
import json
import requests
from parse_openapi import parse_openapi

class TestAgent:
    def __init__(self, api_url="http://localhost:8000", llm_url="http://localhost:11434"):
        self.api_url = api_url
        self.llm_url = llm_url
        self.failed_tests = []
        self.test_cases = []
        
    def generate_test_cases(self, schema):
        """Step 1: Generate test cases from schema"""
        prompt = f"""You are a senior QA automation engineer.

Given this API schema with resolved examples:
{json.dumps(schema, indent=2)}

Generate comprehensive API test cases in STRICT JSON format.

For each endpoint, create test cases for:
1. Valid payload (use example_payload as reference)
2. Missing required fields
3. Invalid data types
4. Empty payload

Each test case must include:
- test_name: descriptive name
- method: HTTP method (GET, POST, etc.)
- path: API endpoint path
- payload: actual JSON data (NOT schema references)
- expected_status: HTTP status code

IMPORTANT:
- Use REAL data values, not schema references like $ref
- For strings use actual text like "John Doe"
- For integers use actual numbers like 25
- Output ONLY valid JSON array
- NO markdown, explanations, or comments

Example format:
[
  {{
    "test_name": "test_create_user_valid",
    "method": "POST",
    "path": "/users",
    "payload": {{"name": "John Doe", "age": 25}},
    "expected_status": 200
  }}
]"""
        
        response = requests.post(f"{self.llm_url}/api/generate",
                               json={"model": "llama3", "prompt": prompt, "stream": False})
        
        try:
            response_text = response.json()["response"]
            print(f"LLM response: {response_text[:200]}...")
            
            # Clean up markdown and explanations
            lines = response_text.split('\n')
            json_lines = []
            in_json = False
            
            for line in lines:
                if line.strip().startswith('[') or in_json:
                    in_json = True
                    json_lines.append(line)
                    if line.strip().endswith(']'):
                        break
            
            clean_json = '\n'.join(json_lines)
            test_cases = json.loads(clean_json)
            self.test_cases = test_cases
            return test_cases
        except Exception as e:
            print(f"❌ Failed to parse test cases: {e}")
            # Fallback test cases based on schema
            fallback_cases = []
            # for endpoint in schema:
            #     if endpoint['method'] == 'POST' and endpoint['example_payload']:
            #         fallback_cases.extend([
            #             {
            #                 "test_name": f"test_{endpoint['path'].replace('/', '_')}_valid",
            #                 "method": endpoint['method'],
            #                 "path": endpoint['path'],
            #                 "payload": endpoint['example_payload'],
            #                 "expected_status": 200
            #             },
            #             {
            #                 "test_name": f"test_{endpoint['path'].replace('/', '_')}_empty",
            #                 "method": endpoint['method'],
            #                 "path": endpoint['path'],
            #                 "payload": {},
            #                 "expected_status": 422
            #             }
            #         ])
            return fallback_cases
      
    
    def generate_pytest_code(self, test_cases):
        """Step 2: Convert test cases to pytest code"""
        prompt = f"""Convert these test cases to pytest code:
{json.dumps(test_cases, indent=2)}

Rules:
- Import requests
- Use BASE_URL = "http://localhost:8000"
- Create complete pytest functions with descriptive names
- Use the EXACT method, path, payload, and expected_status from test cases
- Use requests.post(), requests.get(), etc. for HTTP calls
- Construct full URL using BASE_URL + path
- Assert response.status_code == expected_status
- Output ONLY Python code
- NO explanations, markdown, or comments

Example format:
import requests

BASE_URL = "http://localhost:8000"

def test_create_user_valid():
    response = requests.post(BASE_URL + "/users", json={{"name": "John", "age": 25}})
    assert response.status_code == 200"""
        
        response = requests.post(f"{self.llm_url}/api/generate",
                               json={"model": "llama3", "prompt": prompt, "stream": False})
        
        code = response.json()["response"]
        
        # Clean up markdown
        lines = code.split('\n')
        python_lines = []
        in_code = False
        
        for line in lines:
            if line.strip() == '```python' or line.strip() == '```':
                in_code = not in_code
                continue
            if in_code or (line.strip().startswith('import') or line.strip().startswith('def ') or line.strip().startswith('    ') or line.strip().startswith('BASE_URL')):
                python_lines.append(line)
        
        return '\n'.join(python_lines)
    
    def execute_tests(self, test_file="test_api.py"):
        """Step 3: Execute pytest and capture results"""
        result = subprocess.run(["python", "-m", "pytest", test_file, "-v"], 
                              capture_output=True, text=True)
        print(f"Test output: {result.stdout}")
        if result.stderr:
            print(f"Test errors: {result.stderr}")
        return result.returncode == 0, result.stdout, result.stderr
    
    def analyze_failures(self, stderr):
        self.failed_tests.append(stderr)
        
    def run_cycle(self):
        schema = parse_openapi()
        
        for attempt in range(3):
            print(f"\n🔄 Attempt {attempt + 1}")
            
            # Step 1: Generate test cases
            print("📝 Generating test cases...")
            test_cases = self.generate_test_cases(schema)
            print(f"Generated {len(test_cases) if test_cases else 0} test cases")
            
            # Step 2: Generate pytest code
            print("🐍 Generating pytest code...")
            pytest_code = self.generate_pytest_code(test_cases)
            
            with open("test_api.py", "w") as f:
                f.write(pytest_code)
            
            # Step 3: Execute tests
            print("🧪 Executing tests...")
            success, stdout, stderr = self.execute_tests()
            
            if success:
                print("✅ All tests passed!")
                break
            else:
                print(f"❌ Tests failed (attempt {attempt + 1})")
                self.analyze_failures(stderr)

if __name__ == "__main__":
    agent = TestAgent()
    agent.run_cycle()